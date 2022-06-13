import pandas as pd

# Función que genera nuevos indices numericos, desde 0 hasta n-1.
# n: Númmero total de filas del DataFrame
def nuevosIndices(tabla):
    tabla.index=[i for i in range(len(tabla))]
    return tabla

def depurarColumnaIndices(tabla):
    nombrePrimeraCol=tabla.columns[0]
    primeraColumna=tabla[nombrePrimeraCol]
    indices=tabla.index
    if all([indices[i]==primeraColumna[i] for i in indices]):
        tabla=tabla.drop([nombrePrimeraCol],axis=1)
    return tabla

# Función que elimina filas, teniendo en cuenta una columna de valores numéricos.
# Se busca depurar las filas que contengan datos atípicos.
def depurarNumeros(tabla, nombreCol, limInf, limSup):
    indices=tabla.index
    for i in indices:
        fila=tabla.loc[i]
        if fila[nombreCol]<limInf or fila[nombreCol]>limSup:
            tabla=tabla.drop([i],axis=0)
    tabla=nuevosIndices(tabla)
    return tabla

# Función que elimina columnas que tengan un porcentaje de valores indefinidos (NaN) demasiado grande para el problema a tratar.
def depurarColumnas(tabla, porcentaje):
    size=len(tabla)
    columnas=tabla.columns
    for columna in columnas:
        booleanos=tabla[columna].notnull()
        if sum(booleanos)<size*porcentaje:
            tabla=tabla.drop([columna],axis=1)
    tabla=nuevosIndices(tabla)
    return tabla

# Función que da información detallada de cada columna del DataFrame.
# Usar con DataFrames grandes.
def describirColumnas(tabla, factor):
    size=len(tabla)
    columnas=tabla.columns
    for i in range(len(columnas)//factor+1):
        subgrupo=columnas[0+i*factor:factor+i*factor]
        print('*'*85+'SUBGRUPO #'+str(i+1)+'*'*85+'\n')
        print(datos[subgrupo].describe(include='all'))
        input('\nPresione la tecla Enter para mostrar el siguiente subgrupo.\n')

#Función que elimina grupos de columnas innecesarias.
def borrarColumnasInnecesarias(tabla,columnas):
    for columna in columnas:
        tabla=tabla.drop([columna],axis=1)
    return tabla

#Función que desplaza los elementos de una fila hacia la izquierda, entre cierto rango de columnas.
def moverHaciaIzquierda(tabla, posBooleanas, nombreColumna='Unnamed: 89', inicio=6, fin=None):
    columnas=tabla.columns
    if fin is None:
        fin=len(columnas)
    columnas=columnas[inicio:fin]
    for j in range(len(posBooleanas)):
        if posBooleanas[j]:
            aux=tabla.loc[j, columnas[0]]
            for i in range(len(columnas)-1):
                tabla.loc[j, columnas[i]]=tabla.loc[j, columnas[i+1]]
            tabla.loc[j, columnas[i+1]]=aux
    return tabla

#Función que asgina el promedio de los datos numéricos no nulos a las celdas nulas de una columna.
def asignarPromedioNulos(tabla, columna):
    prom=tabla[tabla[columna].notnull()][columna].mean()
    tabla.loc[tabla[columna].isnull(), columna]=prom
    return tabla

#Función que pasa los valores monetarios en cadenas de caracteres a números y cambia el tipo de dato de la columna:
def valoresMonetarios(tabla, columnas):
    for columna in columnas:
        equivalencias={'M':1000000,'K':1000,'B':1000000000}
        booleanos=tabla[columna].notnull()
        for i in range(len(tabla)):
            if booleanos[i]:
                linea=tabla.loc[i,columna]
                if linea=="€ 0":
                    datoNum=0
                else:
                    linea=linea.split('€')[1]
                    datoNum=float(linea[0:-1])
                    escala=linea[-1]
                    datoNum=int(datoNum*equivalencias[escala])
                tabla.loc[i,columna]=str(datoNum)
        tabla[columna]=pd.to_numeric(tabla[columna])
        if booleanos.sum()>0:
            tabla=asignarPromedioNulos(tabla,columna)
        tabla[columna]=tabla[columna].astype('int64')
    return tabla

#Función destinada a devolver los valores únicos que hay en cada columna. Solo es recomendable en casos donde no se presentan muchos valores distintos.
def listaValoresUnicos(tabla, columna):
    lista=[]
    booleanos=tabla[columna].notnull()
    for i in range(len(tabla)):
        if booleanos[i]:
            dato=tabla.loc[i,columna]
            if dato not in lista:
                lista.append(dato)
    return lista

#Función que intercambia dos valores.
def cambiar(a,b):
    aux=a
    a=b
    b=aux
    return a,b

#Función que organiza de mayor a menor dos listas relacionadas.
def sortear(texto, numeros):
    n=len(texto)
    for i in range(n-1):
        for j in range(i+1,n):
            if numeros[i]<numeros[j]:
                numeros[i], numeros[j]=cambiar(numeros[i], numeros[j])
                texto[i], texto[j]=cambiar(texto[i], texto[j])
    return texto, numeros

#Función que devuelve una cantidad estimada de cuantos valores deben agregarse de cada categoría para mantener la proporción de los datos no nulos.
def porcValoresUnicos(tabla, columna):
    lista=listaValoresUnicos(tabla, columna)
    total=tabla[columna].notnull().sum()
    totalNaN=tabla[columna].isnull().sum()
    cantidad=[round(sum(tabla[columna]==valor)/total*totalNaN) for valor in lista]
    lista, cantidad=sortear(lista, cantidad)
    if sum(cantidad)<totalNaN:
        diferencia=totalNaN-sum(cantidad)
        cantidad[0]+=diferencia
    return lista, cantidad

#Función que llena una columna categórica con una aproximación de las veces que debe estar cada valor para elimnar los valores nulos.
def llenarValoresCategoricos(tabla, columna):
    lista, cantidad=porcValoresUnicos(tabla, columna)
    booleanos=tabla[columna].isnull()
    contador=0
    for i in range(len(tabla)):
        if booleanos[i]:
            contador+=1
            tabla.loc[i,columna]=lista[0]
            if contador==cantidad[0]:
                lista.pop(0)
                cantidad.pop(0)
                contador=0
    return tabla

#Columnas para borrar sin problema: 'Unnamed: 0', 'ID', 'Photo', 'Unnamed: 89'
#Nota: La última columna hay que revisarla para mover unos datos.
datos=pd.read_csv('fifa.csv')
columnasParaBorrar=['Unnamed: 0','ID','Photo']
datos=borrarColumnasInnecesarias(datos, columnasParaBorrar)

#Se soluciona el problema de los valores faltantes en la nacionalidad gracias al dato de la bandera y luego se borra la columna 'Flag'
booleanos=datos['Nationality'].isnull()
for i in range(len(booleanos)):
    if booleanos[i]:
        bandera=datos.loc[i,'Flag']
        grupo=datos.loc[datos['Flag']==bandera,'Nationality']
        grupo=grupo[grupo.notnull()]
        datos.loc[i,'Nationality']=grupo.iloc[0]
datos=datos.drop(['Flag'],axis=1)

#Se soluciona el problema de los valores faltantes en los clubes gracias al dato del logo y luego se borra la columna 'Club Logo'
booleanos=datos['Club'].isnull()
contEqInv=1
for i in range(len(booleanos)):
    if booleanos[i]:
        bandera=datos.loc[i,'Club Logo']
        grupo=datos.loc[datos['Club Logo']==bandera,'Club']
        grupo=grupo[grupo.notnull()]
        if grupo.empty:
            datos.loc[i,'Club']=f'Equipo Inventado {contEqInv} FC'
            contEqInv+=1
        else:
            datos.loc[i,'Club']=grupo.iloc[0]
datos=datos.drop(['Club Logo'],axis=1)

#Se soluciona el problema de los datos desplazados y se elimina la columna 'Unnamed: 89'
datos=moverHaciaIzquierda(datos, datos['Unnamed: 89'].notnull())
datos=datos.drop(['Unnamed: 89'],axis=1)

#La fila del 15352vo registro también debe desplazarse a la izquierda.
columnas=datos.columns[6:]
for i in range(len(columnas)-1):
    datos.loc[15352, columnas[i]]=datos.loc[15352, columnas[i+1]]
datos.loc[15352, columnas[i+1]]="€ 0"

#Se borra la columna: 'Real Face'
datos=datos.drop(['Real Face'],axis=1)

#Se toman las edades entre 15 y 100 como datos válidos y se halla un promedio de estos datos.
#Posteriormente se reemplaza en aquellas filas con datos atípicos.
subconjunto=datos[(datos['Age']>15) & (datos['Age']<100)] #Es necesario usar el ampersand y símbolos similares para realizar operaciones lógicas.
promEdades=int(subconjunto['Age'].mean()//1)

#.loc y .iloc permiten realizar el cambio de un valor dado un condicional o ubicaciones. 
#.replace se usa para cambiar valores específicos (el método se encarga de buscar sus posiciones).
datos.loc[(datos['Age']<15) | (datos['Age']>100),'Age']=promEdades

#Columnas con valores monetarios: 'Value', 'Wage', 'Release Clause'
columnasMonetarias=['Value', 'Wage', 'Release Clause']
datos=valoresMonetarios(datos,columnasMonetarias)

#Primero se modifica la columna con la altura pasandolo de pies y pulgadas a metros.
booleanos=datos['Height'].notnull()
for i in range(len(datos)):
    if booleanos[i]:
        pie=0.3048
        pulgada=0.0254
        linea=datos.loc[i,'Height']
        linea=linea.split('\'')
        altura=int(linea[0])*pie+int(linea[1])*pulgada
        altura=f'{altura:.2f}'
        datos.loc[i,'Height']=altura
datos['Height']=pd.to_numeric(datos['Height'])
datos=asignarPromedioNulos(datos,'Height')

#Luego se modifica la columna con el peso en libras pasandolo a kilogramos.
booleanos=datos['Weight'].notnull()
for i in range(len(datos)):
    if booleanos[i]:
        libra=0.453592
        linea=datos.loc[i,'Weight']
        linea=linea.split('lbs')
        peso=int(linea[0])*libra
        peso=f'{peso:.2f}'
        datos.loc[i,'Weight']=peso
datos['Weight']=pd.to_numeric(datos['Weight'])
datos=asignarPromedioNulos(datos,'Weight')

#Columnas con valores categóricos a cambiar: 'Preferred Foot', 'Work Rate', 'Body Type'
columnasCambiar=['Preferred Foot', 'Work Rate', 'Body Type']
for columna in columnasCambiar:
    datos=llenarValoresCategoricos(datos, columna)

#Depurando datos nulos de 'Weak Foot'.
prom=round(datos['Weak Foot'].mean())
booleanos=datos['Weak Foot'].isnull()
datos.loc[booleanos,'Weak Foot']=promEdades

#Se guarda el Dataframe depurado.
datos.to_csv('nuevoFifa.csv')
datos.to_excel('nuevoFifa.xlsx')