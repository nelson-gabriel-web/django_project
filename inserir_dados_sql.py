import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("📊 Inserindo moedas...")

# Inserir moedas (usando INSERT OR IGNORE para evitar duplicatas)
moedas = [
    ('MZN', 'Metical', 'MT', 1.0000, 1, 1),
    ('USD', 'Dólar Americano', '$', 0.0016, 1, 0),
    ('EUR', 'Euro', '€', 0.0015, 1, 0),
]

for m in moedas:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO core_moeda 
            (codigo, nome, simbolo, taxa_cambio, ativa, padrao) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, m)
        print(f'   ✅ {m[0]} inserido')
    except Exception as e:
        print(f'   ⚠️ Erro ao inserir {m[0]}: {e}')

print("\n📂 Inserindo categorias...")

categorias = [
    ('Veículos', '🚗', 'Carros, motos e acessórios', 1),
    ('Eletrônicos', '📱', 'Smartphones, computadores e gadgets', 1),
    ('Imóveis', '🏠', 'Casas, apartamentos e terrenos', 1),
    ('Alimentação', '🍕', 'Comidas e bebidas', 1),
    ('Roupas', '👕', 'Vestuário e calçados', 1),
    ('Serviços', '🔧', 'Serviços profissionais', 1),
]

for c in categorias:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO core_categoria 
            (nome, icone, descricao, ativo) 
            VALUES (?, ?, ?, ?)
        """, c)
        print(f'   ✅ {c[0]} inserido')
    except Exception as e:
        print(f'   ⚠️ Erro ao inserir {c[0]}: {e}')

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ DADOS INSERIDOS COM SUCESSO!")
print("=" * 50)

print("\n📋 AGORA CRIE O ADMIN:")
print("   python manage.py createsuperuser")