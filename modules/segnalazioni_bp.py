"""
ProtezioNET - Modulo Segnalazioni Emergenze per integrazione in appy ANA esistente
NON SOVRASCRIVE appy.py esistente! Si importa come nuovo form!

File: modules/segnalazioni_bp.py

Come integrare in appy.py ANA già presente e funzionante (senza cancellare nulla):

1. Copia questo file in modules/segnalazioni_bp.py nel tuo progetto ANA
2. Copia templates/segnalazioni_emergenze.html in templates/
3. In appy.py esistente, aggiungi 2 righe (vedi integration_snippet.py)

Non cancella nulla, aggiunge solo nuovo form /segnalazioni

Ezio Fiscato - 24/10/2026
"""

from flask import Blueprint, render_template, request, jsonify
import json
import os
from datetime import datetime

# Blueprint per nuovo form segnalazioni - prefisso /segnalazioni
segnalazioni_bp = Blueprint('segnalazioni', __name__, url_prefix='/segnalazioni', template_folder='../templates')

# File dati nella root del progetto (accanto a appy.py)
def get_data_file():
    # Cerca root progetto (dove c'è appy.py)
    possible_paths = [
        os.path.join(os.getcwd(), 'segnalazioni_ana.json'),
        os.path.join(os.path.dirname(__file__), '..', 'segnalazioni_ana.json'),
        os.path.join(os.path.dirname(__file__), 'segnalazioni_ana.json'),
    ]
    for p in possible_paths:
        # Usa primo path esistente o primo come default
        if os.path.exists(p):
            return p
    return possible_paths[0]

def get_icons_file():
    return get_data_file().replace('segnalazioni_ana.json', 'libreria_icone_ana.json')

def load_segnalazioni():
    f = get_data_file()
    if os.path.exists(f):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            return []
    return []

def save_segnalazioni(data):
    try:
        f = get_data_file()
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Errore salvataggio segnalazioni: {e}")
        return False

@segnalazioni_bp.route('/')
def segnalazioni_home():
    """Nuovo form Segnalazioni Emergenze - Route /segnalazioni/"""
    return render_template('segnalazioni_emergenze.html')

@segnalazioni_bp.route('/form')
def segnalazioni_form():
    """Alias /segnalazioni/form"""
    return render_template('segnalazioni_emergenze.html')

@segnalazioni_bp.route('/api/list', methods=['GET'])
def api_list():
    """API GET /segnalazioni/api/list - Lista segnalazioni"""
    data = load_segnalazioni()
    return jsonify({
        'success': True,
        'count': len(data),
        'data': data,
        'module': 'segnalazioni_emergenze',
        'version': 'v15.1 - Schede 118 SX + StreetMap + Icone Esterno'
    })

@segnalazioni_bp.route('/api/save', methods=['POST'])
def api_save():
    """API POST /segnalazioni/api/save - Salva segnalazione"""
    try:
        nuova = request.get_json()
        if not nuova:
            return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
        
        required = ['nome', 'cognome', 'tel', 'via', 'comune', 'tipologia']
        for field in required:
            if not nuova.get(field):
                return jsonify({'success': False, 'error': f'Campo richiesto: {field}'}), 400
        
        segnalazioni = load_segnalazioni()
        
        if not nuova.get('id'):
            nuova['id'] = max([s.get('id', 0) for s in segnalazioni], default=0) + 1
        
        nuova['server_timestamp'] = datetime.now().isoformat()
        nuova['module'] = 'segnalazioni_emergenze'
        
        existing_idx = next((i for i, s in enumerate(segnalazioni) if s.get('id') == nuova.get('id')), None)
        if existing_idx is not None:
            segnalazioni[existing_idx] = nuova
            action = 'aggiornata'
        else:
            segnalazioni.append(nuova)
            action = 'salvata'
        
        if save_segnalazioni(segnalazioni):
            return jsonify({
                'success': True,
                'action': action,
                'id': nuova['id'],
                'message': f'Segnalazione {action} - ID {nuova["id"]} - Modulo ANA'
            })
        else:
            return jsonify({'success': False, 'error': 'Errore salvataggio'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@segnalazioni_bp.route('/api/delete/<int:seg_id>', methods=['DELETE'])
def api_delete(seg_id):
    """API DELETE /segnalazioni/api/delete/<id>"""
    segnalazioni = load_segnalazioni()
    original_len = len(segnalazioni)
    segnalazioni = [s for s in segnalazioni if s.get('id') != seg_id]
    
    if len(segnalazioni) < original_len:
        save_segnalazioni(segnalazioni)
        return jsonify({'success': True, 'message': f'Segnalazione {seg_id} eliminata'})
    else:
        return jsonify({'success': False, 'error': 'Non trovata'}), 404

@segnalazioni_bp.route('/health')
def health():
    """Health check modulo"""
    return jsonify({
        'status': 'operativo',
        'module': 'segnalazioni_emergenze',
        'version': 'v15.1 - Schede 118 SX - StreetMap OSM DE - Icone Esterno',
        'routes': [
            '/segnalazioni/',
            '/segnalazioni/form',
            '/segnalazioni/api/list',
            '/segnalazioni/api/save',
            '/segnalazioni/health'
        ],
        'segnalazioni_count': len(load_segnalazioni()),
        'timestamp': datetime.now().isoformat()
    })
