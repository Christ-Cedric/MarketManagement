from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from decimal import Decimal, InvalidOperation
import json
from .models import Transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from decimal import Decimal, InvalidOperation
import json
from datetime import datetime
from .models import Transaction

# Imports pour le PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def ajouter_transaction(request):
    try:
        data = json.loads(request.body)
        
        # Valider et nettoyer le montant avant de sauvegarder
        montant = data.get('montant', 0)
        if montant == '' or montant is None:
            montant = 0
        
        # Convertir en Decimal de manière sécurisée
        try:
            montant = Decimal(str(montant))
        except (ValueError, InvalidOperation):
            montant = Decimal('0.00')
            
        transaction = Transaction.objects.create(
            nom=data['nom'],
            prenom=data['prenom'],
            CNIB=data['CNIB'],
            type_transaction=data['type_transaction'],
            operateur=data['operateur'],
            montant=montant
        )
        return JsonResponse({
            'success': True,
            'id': transaction.id,
            'message': 'Transaction ajoutée avec succès'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

def get_transactions(request):
    operateur = request.GET.get('operateur', 'all')
    
    print(f"🔍 Paramètre reçu: operateur = '{operateur}'")  # DEBUG
    
    try:
        # Utiliser une requête SQL brute pour contourner l'erreur de conversion
        with connection.cursor() as cursor:
            if operateur == 'all':
                print("📊 Chargement de TOUTES les transactions")  # DEBUG
                cursor.execute("""
                    SELECT 
                        id, 
                        date,
                        nom,
                        prenom,
                        CNIB,
                        type_transaction,
                        operateur,
                        CAST(montant AS TEXT) as montant
                    FROM mon_app_transaction
                    ORDER BY date DESC
                """)
            else:
                print(f"📊 Filtrage pour l'opérateur: '{operateur}'")  # DEBUG
                # Utiliser %s pour les paramètres avec Django
                cursor.execute("""
                    SELECT 
                        id, 
                        date,
                        nom,
                        prenom,
                        CNIB,
                        type_transaction,
                        operateur,
                        CAST(montant AS TEXT) as montant
                    FROM mon_app_transaction
                    WHERE operateur = %s
                    ORDER BY date DESC
                """, [operateur])
            
            transactions_data = []
            row_count = 0
            
            for row in cursor.fetchall():
                row_count += 1
                try:
                    # Récupérer les données
                    transaction_id = row[0]
                    date_val = row[1]
                    nom = row[2] or ''
                    prenom = row[3] or ''
                    cnib = row[4] or ''
                    type_trans = row[5] or ''
                    operateur_val = row[6] or ''
                    montant_str = row[7] or '0'
                    
                    # Convertir le montant de manière sécurisée
                    try:
                        montant = int(float(montant_str))
                    except (ValueError, TypeError):
                        montant = 0
                    
                    transactions_data.append({
                        'id': transaction_id,
                        'date': date_val,
                        'nom': nom,
                        'prenom': prenom,
                        'CNIB': cnib,
                        'type': type_trans,
                        'operateur': operateur_val,
                        'montant': montant
                    })
                except Exception as e:
                    # En cas d'erreur sur une transaction, logger et continuer
                    print(f"❌ Erreur sur transaction ID {row[0]}: {e}")
                    continue
            
            print(f"✅ {row_count} transaction(s) trouvée(s)")  # DEBUG
            print(f"✅ {len(transactions_data)} transaction(s) retournée(s)")  # DEBUG
        
        return JsonResponse({'transactions': transactions_data})
        
    except Exception as e:
        print(f"❌ ERREUR dans get_transactions: {e}")  # DEBUG
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'message': 'Erreur lors de la récupération des transactions'
        }, status=500)
    

@csrf_exempt
@require_http_methods(["POST"])
def export_transactions_pdf(request):
    """
    Exporte les transactions en PDF et les supprime automatiquement de la base
    """
    try:
        data = json.loads(request.body)
        operateur = data.get('operateur', 'all')
        
        print(f"📄 Export PDF demandé pour: {operateur}")
        
        # Récupérer les transactions à exporter avec l'ORM Django
        if operateur == 'all':
            transactions = Transaction.objects.all().order_by('-date')
        else:
            transactions = Transaction.objects.filter(operateur=operateur).order_by('-date')
        
        if not transactions.exists():
            return JsonResponse({
                'success': False,
                'message': 'Aucune transaction à exporter'
            }, status=400)
        
        print(f"📊 {transactions.count()} transaction(s) à exporter")
        
        # Créer le PDF en mémoire
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Centre
        )
        
        # Titre
        title_text = f"Rapport des Transactions"
        if operateur != 'all':
            title_text += f" - {operateur}"
        title = Paragraph(title_text, title_style)
        elements.append(title)
        
        # Date d'export
        date_export = datetime.now().strftime('%d/%m/%Y à %H:%M')
        subtitle = Paragraph(f"<b>Date d'export:</b> {date_export}", styles['Normal'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.5*cm))
        
        # Préparer les données du tableau
        data_table = [['Date', 'Nom', 'Prénom', 'CNIB', 'Type', 'Opérateur', 'Montant (FCFA)']]
        
        total_montant = 0
        ids_to_delete = []
        
        for transaction in transactions:
            try:
                # Récupérer les données via l'ORM
                transaction_id = transaction.id
                date_val = transaction.date
                nom = transaction.nom or ''
                prenom = transaction.prenom or ''
                cnib = transaction.CNIB or ''
                type_trans = transaction.type_transaction or ''
                operateur_val = transaction.operateur or ''
                
                # Gérer le montant de manière sécurisée
                try:
                    if transaction.montant:
                        montant = float(transaction.montant)
                    else:
                        montant = 0
                except (ValueError, TypeError, InvalidOperation):
                    montant = 0
                
                total_montant += montant
                ids_to_delete.append(transaction_id)
                
                # Formater la date
                if isinstance(date_val, str):
                    formatted_date = date_val
                else:
                    formatted_date = date_val.strftime('%d/%m/%Y %H:%M')
                
                data_table.append([
                    formatted_date,
                    nom,
                    prenom,
                    cnib,
                    type_trans,
                    operateur_val,
                    f"{int(montant):,}".replace(',', ' ')
                ])
                
            except Exception as e:
                print(f"⚠️ Erreur sur transaction ID {transaction.id}: {e}")
                continue
        
        # Ligne de total
        data_table.append(['', '', '', '', '', 'TOTAL:', f"{int(total_montant):,}".replace(',', ' ')])
        
        # Créer le tableau
        table = Table(data_table, repeatRows=1)
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corps du tableau
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            
            # Ligne de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (5, -1), (-1, -1), 'CENTER'),
        ]))
        
        elements.append(table)
        
        # Générer le PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        # Supprimer les transactions de la base de données
        if ids_to_delete:
            try:
                # Utiliser l'ORM pour supprimer
                Transaction.objects.filter(id__in=ids_to_delete).delete()
                print(f"🗑️ {len(ids_to_delete)} transaction(s) supprimée(s) de la base")
            except Exception as e:
                print(f"⚠️ Erreur lors de la suppression des transactions: {e}")
        
        # Retourner le PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"transactions_{operateur}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        print(f"✅ Export PDF réussi: {filename}")
        
        return response
        
    except Exception as e:
        print(f"❌ ERREUR lors de l'export PDF: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'export: {str(e)}'
        }, status=500)