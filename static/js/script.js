// Welcome screen simulation
document.addEventListener('DOMContentLoaded', function() {
    const welcomeScreen = document.getElementById('welcomeScreen');
    const mainApp = document.getElementById('mainApp');
    const loadingProgress = document.getElementById('loadingProgress');
    
    // Simulate loading progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += 1;
        loadingProgress.style.width = progress + '%';
        
        if (progress >= 100) {
            clearInterval(interval);
            // Hide welcome screen and show main app
            welcomeScreen.style.opacity = '0';
            setTimeout(() => {
                welcomeScreen.style.display = 'none';
                mainApp.style.display = 'block';
                
                // Charger toutes les transactions après l'affichage de l'application
                loadTransactions('all');
            }, 800);
        }
    }, 30);

        
    
    // Modal functionality
    const newRegisterBtn = document.getElementById('newRegister');
    const popup = document.getElementById('popup');
    const closePopup = document.getElementById('closePopup');
    const depotBtn = document.getElementById('Depot');
    const retraitBtn = document.getElementById('Retrait');
    const formDepot = document.getElementById('formDepot');
    const formRetrait = document.getElementById('formRetrait');
    const closeFormDepot = document.getElementById('closeFormDepot');
    const closeFormRetrait = document.getElementById('closeFormRetrait');
    const annulerBtn = document.getElementById('annuler');
    const annuleBtn = document.getElementById('annule');
    const stats= document.getElementById('stats');
       
    stats.addEventListener('click',function()
    {
        alert('Fonctionnalitê non disponible!!!')
    })
    newRegisterBtn.addEventListener('click', function() {
        popup.style.display = 'block';
    });
    
    closePopup.addEventListener('click', function() {
        popup.style.display = 'none';
    });
    
    depotBtn.addEventListener('click', function() {
        popup.style.display = 'none';
        formDepot.style.display = 'block';
    });
    
    retraitBtn.addEventListener('click', function() {
        popup.style.display = 'none';
        formRetrait.style.display = 'block';
    });
    
    closeFormDepot.addEventListener('click', function() {
        formDepot.style.display = 'none';
    });
    
    closeFormRetrait.addEventListener('click', function() {
        formRetrait.style.display = 'none';
    });
    
    annulerBtn.addEventListener('click', function(e) {
        e.preventDefault();
        formDepot.style.display = 'none';
    });
    
    annuleBtn.addEventListener('click', function(e) {
        e.preventDefault();
        formRetrait.style.display = 'none';
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === popup) {
            popup.style.display = 'none';
        }
        if (event.target === formDepot) {
            formDepot.style.display = 'none';
        }
        if (event.target === formRetrait) {
            formRetrait.style.display = 'none';
        }
    });
    
    // Set today's date as default in date fields
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.value = today;
    });
    
    // Initialiser les écouteurs d'événements pour les boutons d'opérateurs
    initializeOperatorButtons();
});

// Fonction pour initialiser les boutons d'opérateurs
function initializeOperatorButtons() {
    const operatorButtons = document.querySelectorAll('.operator-btn');
    
    operatorButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Mettre à jour l'état actif des boutons
            operatorButtons.forEach(btn => {
                btn.classList.remove('active', 'btn-primary');
                const originalColor = getButtonColor(btn);
                btn.classList.add('btn-outline-' + originalColor);
            });
            
            // Activer le bouton cliqué
            const originalColor = getButtonColor(this);
            this.classList.remove('btn-outline-' + originalColor);
            this.classList.add('btn-primary', 'active');
            
            // Charger les transactions filtrées
            const operator = this.getAttribute('data-operator');
            loadTransactions(operator);
        });
    });
    
    // Activer le bouton "Tous" par défaut
    const allButton = document.querySelector('.operator-btn[data-operator="all"]');
    if (allButton) {
        allButton.classList.remove('btn-outline-light');
        allButton.classList.add('btn-primary', 'active');
    }
}

// Fonction utilitaire pour récupérer la couleur du bouton
function getButtonColor(button) {
    const classes = button.className.split(' ');
    for (let cls of classes) {
        if (cls.startsWith('btn-outline-')) {
            return cls.replace('btn-outline-', '');
        }
    }
    return 'secondary';
}

// Fonction pour récupérer le token CSRF
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fonction pour charger les transactions depuis l'API
async function loadTransactions(operateur = 'all') {
    try {
        const response = await fetch(`/api/transactions/?operateur=${operateur}`);
        const data = await response.json();
        
        if (data.transactions) {
            updateTransactionsTable(data.transactions);
        } else {
            console.error('Erreur lors du chargement des transactions');
            updateTransactionsTable([]);
        }
    } catch (error) {
        console.error('Erreur:', error);
        updateTransactionsTable([]);
    }
}

// Fonction pour mettre à jour le tableau
function updateTransactionsTable(transactions) {
    const tableBody = document.getElementById('productsTable');
    
    if (transactions.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="border text-center py-4"></td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = transactions.map(transaction => `
        <tr data-operateur="${transaction.operateur}">
            <td class="border">${transaction.date}</td>
            <td class="border">${transaction.nom}</td>
            <td class="border">${transaction.prenom}</td>
            <td class="border">${transaction.CNIB}</td>
            <td class="border">${transaction.type}</td>
            <td class="border">${transaction.operateur}</td>
            <td class="border">${transaction.montant} FCFA</td>
        </tr>
    `).join('');
}

// Fonction pour ajouter une transaction via l'API
async function addTransaction(transactionData) {
    try {
        const response = await fetch('/api/transactions/ajouter/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(transactionData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Recharger les transactions après ajout
            const activeOperator = document.querySelector('.operator-btn.active');
            if (activeOperator) {
                const operator = activeOperator.getAttribute('data-operator');
                loadTransactions(operator);
            } else {
                loadTransactions('all');
            }
            return true;
        } else {
            alert('Erreur: ' + result.message);
            return false;
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'ajout de la transaction');
        return false;
    }
}

// Fonction d'enregistrement modifiée pour utiliser l'API
async function enregistrer(form, type) {
    const formData = new FormData(form);
    const nom = formData.get('nom');
    const prenom = formData.get('prenom');
    const CNIB = formData.get('CNIB');
    const Transaction = formData.get('Transaction');
    const Operateur = formData.get('Operateur');
    const date = formData.get('date');
    const Montant = parseFloat(formData.get('Montant'));
    
    // Validation
    if (!nom || !prenom || !CNIB || !Transaction || !Operateur || !date || isNaN(Montant)) {
        alert("Veuillez remplir tous les champs correctement avant d'enregistrer.");
        return false;
    }
    
    if (Montant <= 0) {
        alert("Le montant doit être supérieur à 0.");
        return false;
    }

    // Préparer les données pour l'API
    const transactionData = {
        nom: nom,
        prenom: prenom,
        CNIB: CNIB,
        type_transaction: type,
        operateur: Operateur,
        montant: Montant,
        date: date
    };

    // Utiliser l'API pour ajouter la transaction
    const success = await addTransaction(transactionData);
    
    if (success) {
        alert(`${type} enregistré avec succès !`);
        form.reset();
        // Remettre la date d'aujourd'hui
        const today = new Date().toISOString().split('T')[0];
        form.querySelector('input[type="date"]').value = today;
        return true;
    }
    return false;
}

// Écouteurs pour les boutons d'enregistrement
document.addEventListener('DOMContentLoaded', function() {
    const registerDepot = document.getElementById('RegisterDepot');
    const registerRetrait = document.getElementById('RegisterRetrait');
    
    if (registerDepot) {
        registerDepot.addEventListener('click', async function(e) {
            e.preventDefault();
            const productForm = document.getElementById('formDepot');
            if (await enregistrer(productForm, "Dépôt")) {
                productForm.style.display = 'none';
            }
        });
    }
    
    if (registerRetrait) {
        registerRetrait.addEventListener('click', async function(e) {
            e.preventDefault();
            const retraitForm = document.getElementById('formRetrait');
            if (await enregistrer(retraitForm, "Retrait")) {
                retraitForm.style.display = 'none';
            }
        });
    }
});

// Fonction de filtrage côté client (fallback si l'API ne fonctionne pas)
function filterTransactionsClientSide(operator) {
    const rows = document.querySelectorAll('#productsTable tr');
    let hasVisibleRows = false;
    
    rows.forEach(row => {
        if (row.cells.length > 1) { // Ignorer les lignes vides
            const operatorCell = row.cells[5]; // La 6ème cellule contient l'opérateur
            
            if (operator === 'all' || operatorCell.textContent.trim() === operator) {
                row.style.display = '';
                hasVisibleRows = true;
            } else {
                row.style.display = 'none';
            }
        }
    });
    
    // Afficher un message si aucune ligne n'est visible
    const tableBody = document.getElementById('productsTable');
    if (!hasVisibleRows && rows.length > 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="border text-center py-4"></td>
            </tr>
        `;
    }
}

// Gestion des erreurs de chargement
window.addEventListener('error', function(e) {
    console.error('Erreur globale:', e.error);
});

// Export des fonctions pour un usage global (si nécessaire)
window.loadTransactions = loadTransactions;
window.addTransaction = addTransaction;
window.filterTransactionsClientSide = filterTransactionsClientSide;

// Ajouter cette fonction à votre script.js existant

document.addEventListener('DOMContentLoaded', function() {
    // ... votre code existant ...
    
    // Bouton d'export PDF
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', async function() {
            // Récupérer l'opérateur actif
            const activeButton = document.querySelector('.operator-btn.active');
            const operateur = activeButton ? activeButton.getAttribute('data-operator') : 'all';
            
            // Message de confirmation
            const confirmMessage = operateur === 'all' 
                ? '⚠️ Voulez-vous exporter TOUTES les transactions en PDF ?\n\n⚠️ ATTENTION: Les transactions exportées seront SUPPRIMÉES de la base de données !'
                : `⚠️ Voulez-vous exporter les transactions de ${operateur} en PDF ?\n\n⚠️ ATTENTION: Les transactions exportées seront SUPPRIMÉES de la base de données !`;
            
            if (!confirm(confirmMessage)) {
                return;
            }
            
            // Désactiver le bouton pendant l'export
            exportPdfBtn.disabled = true;
            exportPdfBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Export en cours...';
            
            try {
                const response = await fetch('/api/transactions/export-pdf/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        operateur: operateur
                    })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.message || 'Erreur lors de l\'export');
                }
                
                // Télécharger le PDF
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `transactions_${operateur}_${new Date().getTime()}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                // Message de succès
                alert('✅ Export réussi ! Les transactions ont été supprimées de la base de données.');
                
                // Recharger les transactions (le tableau sera vide)
                loadTransactions(operateur);
                
            } catch (error) {
                console.error('❌ Erreur lors de l\'export:', error);
                alert('❌ Erreur lors de l\'export: ' + error.message);
            } finally {
                // Réactiver le bouton
                exportPdfBtn.disabled = false;
                exportPdfBtn.innerHTML = '<i class="bi bi-file-earmark-pdf me-2"></i> Exporter en PDF';
            }
        });
    }
});