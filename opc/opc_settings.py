from myapp.models import Params

def getDBSettings():
    try:
        
        parametros = Params.objects.all()
        settings = {}

        for p in parametros:
            settings[p.params_id] = p.params_value

        return settings
    except:
        return {}

settings = getDBSettings()
