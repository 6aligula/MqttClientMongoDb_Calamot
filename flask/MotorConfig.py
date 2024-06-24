import threading

class MotorConfig:
    def __init__(self, db):
        self.db = db
        self.collection = db['configuracion_motor']
        self.lock = threading.Lock()
        self.ensure_config_exists()

    def ensure_config_exists(self):
        # Crear la configuración por defecto si no existe
        if self.collection.count_documents({}) == 0:
            self.collection.insert_one({
                'umbral_alto': 26.0,
                'umbral_bajo': 22.0,
                'segundos': 10
            })

    def update(self, umbral_alto, umbral_bajo, segundos):
        with self.lock:
            self.collection.update_one({}, {'$set': {
                'umbral_alto': umbral_alto,
                'umbral_bajo': umbral_bajo,
                'segundos': segundos
            }})

    def get(self):
        with self.lock:
            config = self.collection.find_one({})
            return config['umbral_alto'], config['umbral_bajo'], config['segundos']
