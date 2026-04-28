search_rules = [
    {
  "contract_logic": {
    "vente": {
      "label": "Vente",
      "allowed_property_types": ["appartement", "villa", "terrain", "terrain_agricole", "immeuble", "bureau", "fond_de_commerce"],
      "price_config": { "label": "Budget Total (FCFA)", "placeholder": "Ex: 150 000 000", "step": 1000000 }
    },
    "location": {
      "label": "Location (Longue durée)",
      "allowed_property_types": ["appartement", "villa", "bureau", "entrepot", "chambre", "studio"],
      "price_config": { "label": "Loyer Mensuel (FCFA)", "placeholder": "Ex: 450 000", "step": 25000 }
    },
    "meublee": {
      "label": "Location Meublée",
      "allowed_property_types": ["appartement", "villa", "studio"],
      "price_config": { "label": "Prix / Nuit ou Mois (FCFA)", "placeholder": "Ex: 60 000", "step": 5000 }
    }
  },
  "geo_hierarchy": {
    "senegal": {
      "label": "Sénégal",
      "cities": ["Dakar", "Thiès", "Mbour", "Saint-Louis", "Saly", "Diamniadio", "Ziguinchor"]
    },
    "cote_divoire": {
      "label": "Côte d'Ivoire",
      "cities": ["Abidjan", "Yamoussoukro", "San-Pédro", "Bouaké"]
    },
    "france": {
      "label": "France",
      "cities": ["Paris", "Lyon", "Marseille", "Bordeaux", "Montpellier"]
    }
  }
}
]