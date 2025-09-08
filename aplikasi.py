import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import io

st.set_page_config(
    page_title="TAM Grub Jual Beli Area Lede",
    layout="wide",
    initial_sidebar_state="collapsed"  # sidebar tertutup saat pertama kali dibuka
)

# Lokasi file data
DATA_FILE = "data/hasil_responden.csv"
os.makedirs("data", exist_ok=True)

# Pertanyaan sesuai indikator
questions = {
    "Perceived Usefulness (PU)": [
        "Grup FB Jual Beli Area Lede membantu saya bertransaksi lebih cepat",
        "Grup FB Jual Beli Area Lede meningkatkan efektivitas saya dalam jual beli",
        "Grup FB Jual Beli Area Lede membuat aktivitas jual beli lebih efisien",
        "Grup FB Jual Beli Area Lede meningkatkan performa saya dalam berjualan atau membeli",
        "Grup FB Jual Beli Area Lede mempermudah interaksi dan komunikasi"
    ],
    "Perceived Ease of Use (PEOU)": [
        "Grup FB Jual Beli Area Lede mudah digunakan untuk aktivitas jual beli",
        "Proses interaksi di Grup FB Jual Beli Area Lede sederhana dan mudah dipahami",
        "Grup FB Jual Beli Area Lede membantu saya mencapai tujuan jual beli",
        "Fitur dalam Grup FB Jual Beli Area Lede mudah dipelajari",
        "Grup FB Jual Beli Area Lede mudah diakses kapan saja"
    ],
    "Attitude Toward Using (ATU)": [
        "Saya merasa nyaman menggunakan Grup FB Jual Beli Area Lede untuk jual beli",
        "Saya merasa senang melakukan aktivitas jual beli di Grup FB Jual Beli Area Lede",
        "Saya menilai menggunakan Grup FB Jual Beli Area Lede adalah ide yang baik",
        "Saya memiliki keinginan untuk terus menggunakan Grup FB Jual Beli Area Lede"
    ],
    "Behavioral Intention (BI)": [
        "Saya berniat untuk terus menggunakan Grup FB Jual Beli Area Lede",
        "Saya berniat merekomendasikan Grup FB Jual Beli Area Lede kepada orang lain",
        "Saya berencana untuk lebih sering bertransaksi melalui Grup FB Jual Beli Area Lede",
        "Saya memiliki rencana untuk tetap aktif dalam Grup FB Jual Beli Area Lede"
    ],
    "Actual Technology Use (ATU-Real)": [
        "Saya sering menggunakan Grup FB Jual Beli Area Lede",
        "Saya menggunakan Grup FB Jual Beli Area Lede dalam waktu yang cukup lama",
        "Saya merasa puas terhadap pengalaman menggunakan Grup FB Jual Beli Area Lede",
        "Saya benar-benar menggunakan Grup FB Jual Beli Area Lede untuk aktivitas jual beli online"
    ]
}

# ===================== Login Admin =====================
st.sidebar.title("🔐 Admin Panel")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

# Username & password (bisa dipindah ke st.secrets saat deploy)
ADMIN_USER = "admin"
ADMIN_PASS = "12345"

is_admin = (username == ADMIN_USER and password == ADMIN_PASS)

# ===================== Menu =====================
if is_admin:
    menu = st.sidebar.radio("📌 Menu", ["Isi Kuesioner", "Lihat Hasil (Admin)"])
else:
    menu = "Isi Kuesioner"

# ===================== Isi Kuesioner =====================
if menu == "Isi Kuesioner":
    st.title("📊 Kuesioner TAM - Jual Beli Online di Grup FB Area Lede")

    # Petunjuk
    with st.expander("📖 Petunjuk Pengisian"):
        st.markdown("""
        Silakan isi kuesioner berikut berdasarkan pengalaman Anda menggunakan **Grup FB Jual Beli Area Lede dan sekitarnya**.  
        Gunakan skala berikut untuk menjawab setiap pertanyaan:

        - **1 = Sangat Tidak Setuju**  
        - **2 = Tidak Setuju**  
        - **3 = Netral**  
        - **4 = Setuju**  
        - **5 = Sangat Setuju**
        """)

    nama = st.text_input("Nama Responden (opsional)")
    responses = {}

    # ✅ Pertanyaan harus di dalam blok ini
    for indicator, qs in questions.items():
        st.subheader(indicator)
        responses[indicator] = []
        for q in qs:
            score = st.radio(
                q,
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: {
                    1: "1 - Sangat Tidak Setuju",
                    2: "2 - Tidak Setuju",
                    3: "3 - Netral",
                    4: "4 - Setuju",
                    5: "5 - Sangat Setuju"
                }[x],
                index=None,   # default None, jadi wajib isi
                key=q
            )
            responses[indicator].append(score)

    # ✅ Tombol simpan juga harus di dalam blok
    if st.button("💾 Simpan Jawaban"):
        if any(score is None for scores in responses.values() for score in scores):
            st.error("⚠️ Harap isi semua pertanyaan sebelum menyimpan.")
        else:
            results = {ind: sum(scores) / len(scores) for ind, scores in responses.items()}
            results = {**{k: None for k in questions.keys()}, **results}
            results["Nama"] = nama if nama else f"Responden_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            df = pd.DataFrame([results])

            try:
                old_df = pd.read_csv(DATA_FILE)
                df = pd.concat([old_df, df], ignore_index=True)
            except (FileNotFoundError, pd.errors.EmptyDataError):
                pass

            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Jawaban berhasil disimpan! Terima kasih sudah berpartisipasi 🙏")

# ===================== Lihat Hasil (Admin) =====================
elif menu == "Lihat Hasil (Admin)":
    st.title("📈 Dashboard Hasil Kuesioner TAM")

    try:
        if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
            st.warning("📂 File data kosong, belum ada jawaban tersimpan.")
        else:
            df = pd.read_csv(DATA_FILE)
            st.subheader("📂 Data Responden")
            st.dataframe(df)

            indikator = list(questions.keys())
            available = [col for col in indikator if col in df.columns]
            if available:
                avg_scores = df[available].mean()

                st.subheader("📊 Rata-rata Skor per Indikator TAM")
                st.write(avg_scores)

                fig, ax = plt.subplots()
                avg_scores.plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")
                ax.set_ylabel("Skor Rata-rata")
                ax.set_ylim(1, 5)
                st.pyplot(fig)
            else:
                st.warning("⚠️ Belum ada data indikator yang sesuai.")

            # 🔹 Download sebagai CSV
            st.download_button(
                "⬇️ Download Data CSV",
                df.to_csv(index=False),
                file_name="hasil_responden.csv",
                mime="text/csv"
            )

            # 🔹 Download sebagai Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Hasil Responden")
                writer.close()  # pastikan file selesai ditulis

            st.download_button(
                label="⬇️ Download Data Excel",
                data=buffer.getvalue(),
                file_name="hasil_responden.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Terjadi error saat membaca data: {e}")


