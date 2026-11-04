# Architecture Ariary Numeric

- mobile/ : application Flet (Android-ready)
- backend/ : Django + DRF API /api/v1/
- contracts/ : contrat Solidity minimal (testnet)
- services externes : optionnels, désactivés par défaut

## Modules
accounts, wallet, ledger, payments, blockchain, logistics, customs, notifications, audit

## Sécurité
- Mots de passe hashés (Django)
- Permissions côté serveur
- Variables d'environnement pour secrets
- Solde modifié uniquement côté serveur (transactions atomiques)
- Idempotence sur transferts
- Journal d'audit
- Empreintes SHA-256 automatiques des opérations dans le registre de test
- Mode invité de démonstration (aucun argent réel)
- Interface trilingue FR/MG/EN
