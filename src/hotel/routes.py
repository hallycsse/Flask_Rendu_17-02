from flask import Blueprint, request,jsonify
from .models import Chambre,Client,Reservation
from .database import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/initdb", methods=["POST"])
def initdb():
  chambre101 = Chambre(numero= 101,type="simple",prix=75.00)
  chambre102 = Chambre(numero= 102,type="double",prix=90.00)

  client1 = Client(nom="Benjamin",email="benjamin@gmail.com")
  client2 = Client(nom="Dorothe",email="dorothe@gmail.com")

  resaC1 = Reservation(id_client = 1,id_chambre = 1,date_arrivee = "2024-02-16 13:00:00",date_depart = "2024-02-20 13:00:00")

  db.session.add_all(chambre101)
  db.session.add(chambre102)
  db.session.add(client1)
  db.session.add(client2)
  db.session.add(resaC1)
  db.session.commit()
  return "succes"

@main.route('/api/chambres', methods=["POST"])
def ajouterChambre():
  data = request.get_json()
  
  if not data:
    return jsonify({"error" : "NO DATA"})

  chambre = Chambre(numero=data["numero"], type= data["type"], prix= data["prix"])

  db.session.add(chambre)
  db.session.commit()
  return jsonify({"success": True, "message": "Chambre ajoutée avec succès."})

@main.route("/api/chambres/<int:id>",methods=["PUT"])
def modifierChambre(id):
  data = request.get_json()

  if not data:
    return jsonify({"error" : "NO DATA"})

  chambre = Chambre.query.get_or_404(id)

  if "numero" in data:
    chambre.numero = int(data["numero"])
  if "type" in data:
    chambre.type = data["type"]
  if "prix" in data:
    chambre.prix = float(data["prix"])

  db.session.commit()
  return jsonify({"success": True,"message": "Chambre mise à jour avec succès."})


@main.route("/api/chambres/disponibles")
def chambresDisponibles():
  data = request.get_json()

  if not data:
    return jsonify({"error" : "NO DATA"})

  chambres = Chambre.query.all()

  dateArrivee = datetime.strptime(data["date_arrivee"],"%Y-%m-%d %H:%M:%S")
  dateDepart = datetime.strptime(data["date_depart"],"%Y-%m-%d %H:%M:%S")

  result = []

  for chambre in chambres:
    for resa in chambre.reservations:
      if ((resa.date_arrivee <= dateArrivee and resa.date_depart >= dateArrivee) or not (resa.date_depart <= dateDepart and resa.date_arrivee >= dateDepart)):
        result.append(chambre)

  return str()

@main.route("/api/reservations",methods=["POST"])
def reserver():
  data = request.get_json()

  if not data:
    return jsonify({"error" : "NO DATA"})

  reservation = Reservation(id_client= data["id_client"],id_chambre=data["id_chambre"],date_arrivee=data["date_arrivee"],date_depart=data["date_depart"],statut="checking")

  db.session.add(reservation)
  db.session.commit()

  allReservations = reservation.chambre.reservations.filter(Reservation.id != reservation.id).all()

  if len(allReservations) == 0:
    reservation.statut = "confirmée"
    db.session.add(reservation)
    db.session.commit()
    return jsonify({"succes" : True, "message": "Réservation créée avec succès."})

  for resa in allReservations:
    if((resa.date_arrivee <= reservation.date_arrivee and resa.date_depart >= reservation.date_arrivee) or (resa.date_depart <= reservation.date_depart and resa.date_arrivee >= reservation.date_depart)):
      db.session.delete(reservation)
      db.session.commit()

      return jsonify({"error": "Les dates de réservation sont déjà prises. Veuillez en sélectionner d'autres."})

  reservation.statut = "confirmée"
  db.session.add(reservation)
  db.session.commit()
  return jsonify({"succes" : True, "message": "Réservation créée avec succès."})

@main.route("/api/reservations/<int:id>",methods=["DELETE"])
def annulerReservation(id):
  resa = Reservation.query.get_or_404(id)

  db.session.delete(resa)
  db.session.commit()
  return jsonify({"success": True,"message": "Réservation annulée avec succès."})