from nicegui import ui
from models import HandoverNote
from storage import notes_db
from datetime import datetime
from uuid import uuid4
import json
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

categories = ['Operational Issues', 'Passenger Needs', 'Safety Concerns', 'VIP Travellers']

def load_default_notes():
    path = Path('templates/default_notes.json')
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

default_notes = load_default_notes()

USERNAME = 'rttapi_ITruss'
PASSWORD = '9cab9ea0814d5332f922afa0b9e947b5db625b03'

def station_exists(station_code: str) -> bool:
    """Check if station exists via API."""
    url = f'https://api.rtt.io/api/v1/json/search/{station_code}'
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            data = response.json()
            # If "location" key exists, station exists
            return 'location' in data and data['location'] is not None
        else:
            return False
    except Exception:
        return False

@ui.page('/')
def main():
    with ui.row().classes('items-center gap-4 mb-4'):
        ui.image('static/image.png').classes('w-8 h-8')
        ui.label('Southeastern Relay Handover Tool').classes('text-2xl font-bold')

    note_text = ui.textarea(label='Note', placeholder='Describe the issue...')
    category = ui.select(options=categories, with_input=True).classes('w-40')
    priority = ui.checkbox('High Priority')

    ui.label('Enter nearest station CRS Code').classes('mt-6 font-semibold')
    station_input = ui.input(label='Station CRS code (e.g. WAT)').classes('w-40')
    station_msg = ui.label('').classes('text-sm mt-1')

    def validate_station(e):
        code = station_input.value.strip().upper()
        if not code:
            station_msg.text = ''
            return
        if station_exists(code):
            station_msg.text = f'Station "{code}" found'
        else:
            station_msg.text = f'Station "{code}" does NOT exist'

    station_input.on('blur', validate_station)

    submit = ui.button('Add Note').props('enabled')

    with ui.expansion('Insert Default Note', icon='note'):
        for item in default_notes:
            def add_default(i=item):
                note_text.value = i['text']
                category.value = i['category']
                priority.value = i['priority']
            ui.button(f"{item['category']}: {item['text'][:40]}...", on_click=add_default).classes('w-full')

    with ui.column().classes('w-full'):
        ui.label('Current Handover Notes').classes('text-xl mt-6 font-semibold')
        notes_column = ui.column().classes('w-full')

    def add_note():
        if not note_text.value or not category.value:
            ui.notify('Please fill out the note and select a category.', type='warning')
            return

        note = HandoverNote(
            id=str(uuid4()),
            station_code=station_input.value,
            text=note_text.value,
            category=category.value,
            priority=priority.value,
            timestamp=datetime.now()
        )
        notes_db.append(note)
        display_note(note)
        note_text.value = ''
        category.value = None
        priority.value = False
        station_input.value = ''
        station_msg.text = ''

    def display_note(note: HandoverNote):
        style = 'bg-red-100' if note.priority else 'bg-gray-100'
        with notes_column:
            with ui.row().classes(f'{style} p-2 rounded w-full items-center justify-between'):
                with ui.column():
                    ui.label(f'{note.category}').classes('text-lg font-bold')
                    ui.label(f'Nearest Station: {note.station_code}' if note.station_code else 'No station specified').classes('text-sm font-bold')
                    ui.label(note.text).classes('text-sm')
                ui.label(note.timestamp.strftime('%Y-%m-%d %H:%M')).classes('text-xs text-gray-600')

    for n in notes_db:
        display_note(n)

    submit.on('click', add_note)

ui.run()
