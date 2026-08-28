import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuração da página do App
st.set_page_config(
    page_title="Carteirinha Família Resenha F.C.",
    page_icon="⚽",
    layout="centered"
)

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Exibir logo no topo da página se existir
if os.path.exists("Logo.png"):
    st.image("Logo.png", width=120)

st.title("Família Resenha F.C.")
st.subheader("Gerador Oficial de Carteirinha Virtual de Sócio-Atleta")
st.write("Preencha as informações abaixo para gerar sua carteirinha e baixar o arquivo PNG!")

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
        pe = st.selectbox("Pé Dominante", ["Diestro", "Canhoto", "Ambidestro"])
        teor = st.slider("Teor Alcoólico na Resenha (%) 🍻", 0, 100, 50)

    foto_file = st.file_uploader("Foto do Atleta (Envie da Galeria ou Tire uma Foto)", type=["jpg", "png", "jpeg"])
    
    submitted = st.form_submit_button("Gerar Minha Carteirinha 🎴")

# --- PROCESSAMENTO E GRAVAÇÃO ---
if submitted:
    if not apelido or not camisa:
        st.error("Por favor, preencha pelo menos o Apelido e o Número da Camisa!")
    else:
        # 1. Salvar dados na Planilha do Google Sheets
        try:
            # Ler dados atuais
            existing_data = conn.read(worksheet="Página1", ttl=0)
            
            # Criar nova linha de cadastro
            new_row = {
                "Data Cadastro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Nome": nome if nome else "N/I",
                "Apelido": apelido,
                "Camisa": camisa,
                "Nascimento": nascimento if nascimento else "N/I",
                "Pé Dominante": pe,
                "Cidade UF": cidade_uf,
                "Temporada": inicio,
                "Teor Alcoólico": f"{teor}%"
            }
            
            # Adicionar e atualizar
            updated_df = existing_data.append(new_row, ignore_index=True)
            conn.update(worksheet="Página1", data=updated_df)
            st.success("✅ Atleta registrado com sucesso na base de dados do time!")
        except Exception as e:
            st.warning("Carteirinha gerada! (Nota: Não foi possível sincronizar com a planilha no momento).")

        # 2. Gerar Imagem da Carteirinha
        W, H = 1012, 638
        card = Image.new("RGB", (W, H), (20, 24, 33))
        draw = ImageDraw.Draw(card)

        draw.rectangle([0, 0, W, 110], fill=(15, 23, 42))
        draw.line([(0, 110), (W, 110)], fill=(234, 179, 8), width=5)
        draw.line([(0, H - 15), (W, H - 15)], fill=(234, 179, 8), width=3)

        font_large = ImageFont.load_default()

        text_start_x = 30
        if os.path.exists("logo.png"):
            logo_img = Image.open("logo.png").convert("RGBA")
            logo_img = logo_img.resize((80, 80))
            card.paste(logo_img, (20, 15), logo_img)
            text_start_x = 110

        draw.text((text_start_x, 25), "FAMÍLIA RESENHA F.C.", fill=(250, 204, 21), font=font_large)
        draw.text((text_start_x, 65), "CARTEIRINHA VIRTUAL DE SÓCIO-ATLETA", fill=(203, 213, 225), font=font_large)

        px, py, pw, ph = 40, 140, 220, 270
        if foto_file:
            user_img = Image.open(foto_file).convert("RGB")
            user_img = user_img.resize((pw, ph))
            card.paste(user_img, (px, py))
        else:
            draw.rectangle([px, py, px + pw, py + ph], fill=(30, 41, 59), outline=(234, 179, 8), width=3)
            draw.text((px + 50, py + 120), "SEM FOTO", fill=(148, 163, 184), font=font_large)

        cx, cy, cr = 200, 380, 45
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(234, 179, 8), outline=(15, 23, 42), width=3)
        draw.text((cx - 15, cy - 10), f"#{camisa}", fill=(15, 23, 42), font=font_large)

        draw.text((300, 140), f"APELIDO: {apelido.upper()}", fill=(250, 204, 21), font=font_large)
        draw.text((300, 180), f"NOME: {nome if nome else 'Atleta Resenheiro'}", fill=(226, 232, 240), font=font_large)
        
        draw.text((300, 240), f"PÉ DOMINANTE: {pe}", fill=(255, 255, 255), font=font_large)
        draw.text((300, 280), f"DATA NASC.: {nascimento if nascimento else 'N/I'}", fill=(255, 255, 255), font=font_large)
        
        draw.text((620, 240), f"TEMPORADA INÍCIO: {inicio}", fill=(255, 255, 255), font=font_large)
        draw.text((620, 280), f"CIDADE/UF: {cidade_uf}", fill=(255, 255, 255), font=font_large)

        bx, by, bw, bh = 40, 475, W - 80, 110
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        
        draw.text((bx + 20, by + 15), f"TEOR ALCOÓLICO NA RESENHA: {teor}% 🍻", fill=(250, 204, 21), font=font_large)
        
        bar_w = int((bw - 40) * (teor / 100.0))
        if bar_w > 0:
            bar_color = (34, 197, 94) if teor < 50 else (234, 179, 8) if teor < 80 else (239, 68, 68)
            draw.rectangle([bx + 20, by + 50, bx + 20 + bar_w, by + 80], fill=bar_color)

        st.image(card, caption=f"Carteirinha Virtual - {apelido}", use_column_width=True)
        
        buf = io.BytesIO()
        card.save(buf, format="PNG")
        st.download_button(
            label="📥 Baixar Carteirinha em Alta Resolução (PNG)",
            data=buf.getvalue(),
            file_name=f"Carteirinha_{apelido.replace(' ', '_')}.png",
            mime="image/png"
        )
