# Simulate.py

Simula un sistema de control sobre una sistema de cola de una queue y N servers. El caso que simula es el del un controlador que verifica la longitud de la cola cada X tiempo y a partir de la longitud de la cola, y de su derivada, ajusta la cantidad de servers

Las unidades de tiempo son genéricas ( como en un modelo de colas ), pero es importante parametrizar todo en las mismas unidades

Las claves son las siguientes: 

La función rate devuelve el valor esperado de arribos al sistema por unidad de tiempo. Aumentando este valor se aumenta la carga general del sistema. Los arribos siguen una distribución poisson con la media de arribos por unidad de tiempo indicados en el este valor
```
def rate(t):
        return 50
```

La función ser_f determina el tiempo de servicio, es decir, el tiempo que tarda un agente en ser servido por el canal. Usamos una distribución exponencial a la que le indicamos la media. En este caso, la media será de 0.8 unidades de tiempo por agente. 
```
def ser_f(t):
        res = t + np.random.exponential(0.8)
        return res

```

En la invocación de la función simulate_control se indican los parámetros: 
simulate_control(qn,time_between_checks, cycles):

.time_between_checks: la cantidad de tiempo que pasa entre checks del controlador
. cycles: la cantidad de ciclos a simular


Por ultimo, existe una función que controla los movimientos de servers para arriba y hacia abajo. En este ejemplo, es la función calculate_new_servers_v2




## TODOs
. En la vida real, no existe  el span instantaneo, por lo que para hacer una simulación más precisa lo ideal es establecer un delay entre el momento de creación de los servers y el momento en que los servers efectivamente se vuelven operativos, ahora es instantaneo
. Generar una dataframe para analizar los resultados con un notebook
. Generar un mejor sistema de parametrización 
