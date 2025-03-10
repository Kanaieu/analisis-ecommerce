import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
import seaborn as sns
import unicodedata
import folium
from branca.colormap import linear
from folium.plugins import HeatMap
from streamlit_folium import st_folium

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe
all_df = pd.read_csv("https://raw.githubusercontent.com/Kanaieu/analisis-ecommerce/main/dashboard/all_data.csv")

# Judul Dashboard
st.title("Dashboard Analisis Revenue dan Keterlambatan Pengiriman dari e-commerce di Brazil")

# === Diagram Bar: Top 10 Kota dengan Revenue Terbesar & Terkecil ===
st.subheader("Top 10 Kota di Brazil dengan Revenue Terbesar & Terkecil")
st.write("Berikut adalah kota-kota di Brazil dengan revenue terbesar dan terkecil berdasarkan transaksi order yang tercatat. Kota dengan revenue tertinggi Sao Paulo, yang berada di pusat ekonomi dan kemungkinan memiliki lebih banyak pelanggan potensial, sementara kota dengan revenue terendah ada di Palotina yang memiliki populasi yang kecil, sehingga jumlah transaksi yang lebih sedikit dan atau jumlah toko online yang lebih sedikit.")

# Ambil 10 kota dengan revenue terbesar
top_10_revenue_cities = all_df.nlargest(10, 'price')

# Ambil 10 kota dengan revenue terkecil
bottom_10_revenue_cities = all_df.nsmallest(10, 'price')

# Format angka menjadi jutaan
def format_million(x, _):
    return f'R${x/1_000_000:.1f}Jt'

top_colors = ['#3974FE'] + ['#9AC9FF'] * (len(top_10_revenue_cities) - 1)
bottom_colors = ['#E52020'] + ['#FAA8A8'] * (len(bottom_10_revenue_cities) - 1)

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Plot revenue terbesar
sns.barplot(
    data=top_10_revenue_cities, 
    x='price', 
    y='seller_city', 
    ax=axes[0]
)
axes[0].set_title('Top 10 Kota dengan Revenue Terbesar (Dalam Jutaan BRL)', fontsize=14)
axes[0].set_xlabel('Total Revenue (BRL)', fontsize=14)
axes[0].set_ylabel('Kota', fontsize=14)
axes[0].xaxis.set_major_formatter(ticker.FuncFormatter(format_million))  # Format ke juta
axes[0].tick_params(axis='y', labelsize=13)
axes[0].tick_params(axis='x', labelsize=13)

for bar, color in zip(axes[0].patches, top_colors):
    bar.set_color(color)

# Plot revenue terkecil
sns.barplot(
    data=bottom_10_revenue_cities, 
    x='price', 
    y='seller_city', 
    ax=axes[1]
)
axes[1].set_title('Top 10 Kota dengan Revenue Terkecil (BRL)', fontsize=14)
axes[1].set_xlabel('Total Revenue (BRL)', fontsize=14)
axes[1].set_ylabel('Kota', fontsize=14)
axes[1].invert_xaxis()
axes[1].yaxis.set_label_position("right") 
axes[1].yaxis.tick_right()
axes[1].tick_params(axis='y', labelsize=13) 
axes[1].tick_params(axis='x', labelsize=13)

for bar, color in zip(axes[1].patches, bottom_colors):
    bar.set_color(color)
    
fig.suptitle('Analisis Kota dengan Revenue Penjualan Tertinggi dan Terendah di Brasil (BRL)', fontsize=22)
plt.tight_layout()

st.pyplot(fig)

# === Peta Kota dengan Keterlambatan Pengiriman Terbesar ===
st.subheader("Peta Kota dengan Rata-Rata Keterlambatan Pengiriman Tertinggi")
st.write("Peta berikut menampilkan kota-kota dengan rata-rata waktu keterlambatan pengiriman tertinggi. Kota dengan warna merah lebih pekat menunjukkan waktu keterlambatan yang lebih tinggi. Disini hanya dicantumkan 20 kota yang memiliki rata rata delay tertinggi. Kota yang terlihat di peta mayoritas bukan kota besar")

top_20_cities = all_df.nlargest(20, 'delivery_delay')

# Mewarnai peta dengan warna sesuai dengan keterlambatan
colormap = linear.YlOrRd_09.scale(top_20_cities['delivery_delay'].min(), top_20_cities['delivery_delay'].max())

# Buat peta Brazil
map_brazil = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# Tambahkan marker untuk 10 kota dengan keterlambatan tertinggi
for index, row in top_20_cities.iterrows():
    folium.CircleMarker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        radius=16, 
        color=colormap(row['delivery_delay']),
        fill=True,
        fill_color=colormap(row['delivery_delay']),
        fill_opacity=0.6
    ).add_to(map_brazil)

# Tambahkan colormap ke peta
colormap.add_to(map_brazil)

# Tampilkan peta
st_folium(map_brazil, width=700, height=500)

# === Heatmap Keterlambatan Pengiriman ===
st.subheader("Heatmap Distribusi Keterlambatan Pengiriman")
st.write("Heatmap ini menunjukkan distribusi keterlambatan pengiriman di berbagai kota. Warna yang lebih merah menunjukkan area dengan tingkat frekuensi keterlambatan yang lebih tinggi. Terlihat lebih banyak kota pesisir yang mengalami keterlambatan pengiriman. Dan lebih sering di kota pesisir bagian tengah dan utara jika dibandingkan dengan yang di selatan")

# Ambil 250 kota dengan keterlambatan tertinggi
top_250_cities = all_df.nlargest(250, 'delivery_delay')

# Pastikan tidak ada nilai NaN sebelum membuat heatmap
heat_data = top_250_cities[['geolocation_lat', 'geolocation_lng', 'delivery_delay']].dropna().values.tolist()

# Buat peta Brazil
heatmap_brazil = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# Tambahkan heatmap ke peta
HeatMap(heat_data, radius=15, blur=10, max_zoom=4).add_to(heatmap_brazil)

# **Gunakan `st_folium` untuk menampilkan peta di Streamlit**
st_folium(heatmap_brazil, width=700, height=500)

st.write("\n---\n")
st.write("Dashboard ini membantu kita memahami pola revenue dan keterlambatan pengiriman di berbagai kota. Data ini dapat digunakan untuk membuat strategi pemasaran di kota Sao Paulo dan kota besar lainnya yang memiliki potensi pasar yang besar. Selain itu, dapat membuat strategi promosi atau subsidi pengiriman yang dapat menjadi cara untuk meningkatkan transaksi di Palotina dan wilayah lain yang minim transaksi")
st.write("Dari data peta dan heatmap dapat disimpulkan daerah pelanggan dengan tingkat keterlambatan tertinggi berada di wilayah terpencil atau wilayah yang memiliki akses terbatas dari daerah kota-kota besar. Menggunakan data ini data ini bisa memberikan estimasi waktu pengiriman yang lebih akurat, sehingga meningkatkan kepuasan pelanggan.")

st.caption('Copyright © Muhammad Tsaqiif Ash-Shiddiq 2025')
