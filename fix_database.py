import sqlite3
import os

# Chemin vers votre base de données
db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print(f"Erreur: {db_path} n'existe pas!")
    print("Vérifiez le chemin de votre base de données.")
    exit(1)

try:
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Connexion à la base de données réussie!\n")
    
    # 1. Identifier le nom exact de la table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%transaction%';")
    tables = cursor.fetchall()
    print("Tables trouvées:", tables)
    
    if not tables:
        print("\nAucune table de transaction trouvée!")
        exit(1)
    
    table_name = tables[0][0]
    print(f"\nUtilisation de la table: {table_name}\n")
    
    # 2. Voir les colonnes de la table
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print("Colonnes de la table:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 3. Trouver les colonnes décimales
    decimal_columns = []
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        if 'DECIMAL' in col_type or 'NUMERIC' in col_type or col_name in ['montant', 'commission', 'frais', 'prix']:
            decimal_columns.append(col_name)
    
    print(f"\nColonnes décimales trouvées: {decimal_columns}\n")
    
    # 4. Vérifier les valeurs invalides
    for col in decimal_columns:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE {col} = '' OR {col} IS NULL OR typeof({col}) = 'text'
        """)
        count = cursor.fetchone()[0]
        print(f"Valeurs invalides dans '{col}': {count}")
    
    # 5. Corriger toutes les valeurs invalides
    print("\nCorrection en cours...")
    total_fixed = 0
    
    for col in decimal_columns:
        cursor.execute(f"""
            UPDATE {table_name} 
            SET {col} = 0.0 
            WHERE {col} = '' OR {col} IS NULL OR typeof({col}) = 'text'
        """)
        fixed = cursor.rowcount
        total_fixed += fixed
        print(f"  - {col}: {fixed} enregistrements corrigés")
    
    # 6. Sauvegarder les modifications
    conn.commit()
    print(f"\n✓ Total: {total_fixed} valeurs corrigées!")
    
    # 7. Vérification finale
    print("\nVérification finale...")
    for col in decimal_columns:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE {col} = '' OR {col} IS NULL OR typeof({col}) = 'text'
        """)
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  ⚠ {col}: {count} valeurs encore invalides")
        else:
            print(f"  ✓ {col}: OK")
    
    # 8. Afficher quelques exemples
    print("\nExemples de données (5 premières lignes):")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    
    # Obtenir les noms de colonnes
    col_names = [description[0] for description in cursor.description]
    print("\n" + " | ".join(col_names))
    print("-" * 80)
    for row in rows:
        print(" | ".join(str(x) for x in row))
    
except sqlite3.Error as e:
    print(f"Erreur SQLite: {e}")
    
except Exception as e:
    print(f"Erreur: {e}")
    
finally:
    if conn:
        conn.close()
        print("\n✓ Connexion fermée")

print("\n" + "="*50)
print("Script terminé! Vous pouvez maintenant relancer votre serveur Django.")
print("="*50)