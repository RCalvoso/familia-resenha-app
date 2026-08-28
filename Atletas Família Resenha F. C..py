import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import requests
from datetime import datetime

# Configuração da página do App
st.set_page_config(
    page_title="Carteirinha Família Resenha F.C.",
    page_icon="⚽",
    layout="centered"
)

# URL do Web App do Google Apps Script (Substitua pela sua URL)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyIaKpFo3M48uYN-f5FFX6DA10c-OKaQYCE7RpH_tdbPqGSbjmTLiMOI1i-JjBi3zu_tA/exec"

# Busca do arquivo de Logo
logo_path = None
for possible_name in ["Logo.png", "logo.png", "logo.png.jfif", "Logo.PNG"]:
    if os.path.exists(possible_name):
        logo_path = possible_name
        break

if logo_path:
    st.image(logo_path, width=120)

st.title("Família Resenha F.C.")
st.subheader("Gerador Oficial de Carteirinha Virtual de Sócio-Atleta")
st.write("Preencha as informações abaixo para gerar sua carteirinha e baixar o arquivo PNG!")

# Carregamento de Fontes
def load_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

font_title = load_font(28, bold=True)
font_subtitle = load_font(18, bold=True)
font_label = load_font(18, bold=True)
font_value = load_font(20, bold=False)
font_badge = load_font(34, bold=True)

# --- FORMULÁRIO DE CADASTRO DO JOGADOR ---
with st.form("form_carteirinha"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome Completo", placeholder="Ex: João da Silva")
        apelido = st.text_input("Apelido na Resenha *", placeholder="Ex: Brunão Artilheiro")
        nascimento = st.text_input("Data de Nascimento", placeholder="Ex: 15/08/1990")
        cidade_uf = st.text_input("Cidade / UF", value="São Paulo / SP")
        
    with col2:
        camisa = st.text_input("Número da Camisa *", placeholder="Ex: 10")
        inicio = st.text_input("Temporada de Início", value="2026")
        pe = st.selectbox("Pé Dominante", ["Destro", "Canhoto", "Ambidestro"])
        teor = st.slider("Teor Alcoólico na Resenha (%) 🍻", 0, 100, 75)

    foto_file = st.file_uploader("Foto do Atleta (Envie da Galeria ou Tire uma Foto)", type=["jpg", "png", "jpeg"])
    
    submitted = st.form_submit_button("Gerar Minha Carteirinha 🎴")

# --- PROCESSAMENTO E GRAVAÇÃO ---
if submitted:
    if not apelido or not camisa:
        st.error("Por favor, preencha pelo menos o Apelido e o Número da Camisa!")
    else:
        # 1. Envio Direto para o Google Sheets via API Web App
        payload = {
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "nome": nome if nome else "N/I",
            "apelido": apelido,
            "camisa": camisa,
            "nascimento": nascimento if nascimento else "N/I",
            "pe": pe,
            "cidade_uf": cidade_uf,
            "temporada": inicio,
            "teor": f"{teor}%"
        }
        
        try:
            res = requests.post(WEB_APP_URL, json=payload, timeout=5)
            if res.status_code == 200:
                st.success("✅ Atleta registrado com sucesso na planilha do Google Drive!")
            else:
                st.info("Carteirinha gerada com sucesso!")
        except Exception:
            st.info("Carteirinha gerada com sucesso!")

        # 2. Gerar Imagem da Carteirinha
        W, H = 1012, 638
        card = Image.new("RGB", (W, H), (20, 24, 33))
        draw = ImageDraw.Draw(card)

        # Cabeçalho e Linhas em Dourado
        draw.rectangle([0, 0, W, 110], fill=(15, 23, 42))
        draw.line([(0, 110), (W, 110)], fill=(234, 179, 8), width=5)
        draw.line([(0, H - 15), (W, H - 15)], fill=(234, 179, 8), width=3)

        text_start_x = 30
        if logo_path:
            logo_img = Image.open(logo_path).convert("RGBA")
            logo_img = logo_img.resize((80, 80))
            card.paste(logo_img, (20, 15), logo_img)
            text_start_x = 115

        # Títulos
        draw.text((text_start_x, 22), "FAMÍLIA RESENHA F.C.", fill=(250, 204, 21), font=font_title)
        draw.text((text_start_x, 65), "CARTEIRINHA VIRTUAL DE SÓCIO-ATLETA", fill=(203, 213, 225), font=font_subtitle)

        # Foto
        px, py, pw, ph = 40, 140, 220, 270
        if foto_file:
            user_img = Image.open(foto_file).convert("RGB")
            user_img = user_img.resize((pw, ph))
            card.paste(user_img, (px, py))
        else:
            draw.rectangle([px, py, px + pw, py + ph], fill=(30, 41, 59), outline=(234, 179, 8), width=3)
            draw.text((px + 50, py + 120), "SEM FOTO", fill=(148, 163, 184), font=font_label)

        # Número da Camisa
        cx, cy, cr = 200, 380, 45
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(234, 179, 8), outline=(15, 23, 42), width=3)
        draw.text((cx - 20, cy - 18), f"#{camisa}", fill=(15, 23, 42), font=font_badge)

        # Dados do Jogador
        draw.text((300, 135), f"APELIDO: {apelido.upper()}", fill=(250, 204, 21), font=font_title)
        draw.text((300, 180), f"NOME: {nome if nome else 'Atleta Resenheiro'}", fill=(226, 232, 240), font=font_value)
        
        draw.text((300, 240), f"PÉ DOMINANTE: {pe}", fill=(255, 255, 255), font=font_value)
        draw.text((300, 285), f"DATA NASC.: {nascimento if nascimento else 'N/I'}", fill=(255, 255, 255), font=font_value)
        
        draw.text((620, 240), f"TEMPORADA INÍCIO: {inicio}", fill=(255, 255, 255), font=font_value)
        draw.text((620, 285), f"CIDADE/UF: {cidade_uf}", fill=(255, 255, 255), font=font_value)

        # Barra do Teor Alcoólico 3D
        bx, by, bw, bh = 40, 470, W - 80, 120
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        
        draw.text((bx + 20, by + 12), "TEOR ALCOÓLICO NA RESENHA", fill=(250, 204, 21), font=font_label)
        draw.text((bx + bw - 100, by + 12), f"{teor}%", fill=(250, 204, 21), font=font_label)
        
        rx, ry, rw, rh = bx + 20, by + 50, bw - 40, 45
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(15, 23, 42), outline=(100, 116, 139), width=2)
        
        bar_w = int((rw - 6) * (teor / 100.0))
        if bar_w > 0:
            if teor < 50:
                base_color, light_color, shadow_color = (34, 197, 94), (134, 239, 172), (21, 128, 61)
            elif teor < 80:
                base_color, light_color, shadow_color = (234, 179, 8), (253, 224, 71), (161, 98, 7)
            else:
                base_color, light_color, shadow_color = (239, 68, 68), (252, 165, 165), (185, 28, 28)

            bx1, by1 = rx + 3, ry + 3
            bx2, by2 = rx + 3 + bar_w, ry + rh - 3
            draw.rectangle([bx1, by1, bx2, by2], fill=base_color)
            
            mid_h = (by2 - by1) // 2
            draw.rectangle([bx1, by1, bx2, by1 + mid_h], fill=light_color)
            draw.rectangle([bx1, by1 + mid_h, bx2, by2], fill=shadow_color)
            draw.line([(bx1, by1), (bx2, by1)], fill=(255, 255, 255), width=2)

        st.image(card, caption=f"Carteirinha Virtual - {apelido}", use_container_width=True)
        
        buf = io.BytesIO()
        card.save(buf, format="PNG")
        st.download_button(
            label="📥 Baixar Carteirinha em Alta Resolução (PNG)",
            data=buf.getvalue(),
            file_name=f"Carteirinha_{apelido.replace(' ', '_')}.png",
            mime="image/png"
        )
