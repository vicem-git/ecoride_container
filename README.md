


Documentation de déploiement (VPS)

Pour déployer l’application sur un VPS :

- Cloner le dépôt sur le VPS

- définir des mots de passe forts pour l'utilisateur postgres et l'application flask


Lancer les services via Docker :

docker compose up --build -d

Accéder à la base PostgreSQL via psql ou un outil graphique

Vérifier que l’application tourne sur localhost:5000 

main.py :
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=false)

S’assurer que les fichiers statiques sont servis correctement depuis Flask ou via Nginx.
