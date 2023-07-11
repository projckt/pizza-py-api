import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rdflib import Graph
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

dirname = os.path.dirname(__file__)
owl_file_path = os.path.join(dirname, 'ontology/pizza.owl')
g = Graph()
g.parse(owl_file_path)

# PYTHON TEST
@app.get("/python")
async def python_test():
    return "Python Test"

# GET TOPPINGS
@app.get("/toppings")
async def get_toppings():
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>

        SELECT ?toppings WHERE { ?toppings rdfs:subClassOf+ pizza:PizzaTopping }
    """
    results = g.query(query) 
    
    toppings = []
    for row in results:
        uri = row["toppings"]
        name = uri.split("#")[1]
        toppings.append(name)

    return_obj = {
        "success": True,
        "payload": toppings
    }

    return return_obj

# GET COUNTRIES
@app.get("/countries")
async def get_countries():
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>

        SELECT ?countries WHERE { ?countries rdf:type pizza:Country }
    """
    results = g.query(query)

    countries = []
    for row in results:
        uri = row["countries"]
        name = uri.split("#")[1]
        countries.append(name)
    
    return_obj = {
        "success": True,
        "payload": countries
    }

    return return_obj

# GET PIZZAS
@app.get("/pizzas")
async def get_pizzas():
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>

        SELECT ?pizzas WHERE { ?pizzas rdfs:subClassOf+ pizza:NamedPizza }
    """
    results = g.query(query) 

    pizzas = []
    for row in results:
        uri = row["pizzas"]
        pizza = uri.split("#")[1]
        pizzas.append(pizza)

    return_obj = {
        "success": True,
        "payload": pizzas
    }

    return return_obj

# GET TOPPINGS BY PIZZA
class Pizza(BaseModel):
    name:str

@app.post("/toppings-by-pizza")
async def get_toppings_by_pizza(pizza:Pizza):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>

        
        SELECT ?name ?topping ?spice
                    WHERE { 
                                    ?name  rdfs:subClassOf pizza:NamedPizza  ;
                                            rdfs:subClassOf ?pizzaDetails . 
                                    ?pizzaDetails owl:someValuesFrom ?topping .
                                    ?topping rdfs:subClassOf ?toppingProp . 
                                    ?toppingProp owl:someValuesFrom ?spice
                    }
    """
    results = g.query(query)

    toppings = []
    for row in results:
        name = row["name"]
        name = name.split("#")
        name = name[1]
        topping = row["topping"]
        topping = topping.split("#")
        topping = topping[1]
        spice = row["spice"]
        spice = spice.split("#")
        spice = spice[1]

        if pizza.name == name:
            pizza_details = {"name": name, "topping": topping, "spice": spice}
            toppings.append(pizza_details)
    
    return { "success": True, "payload": toppings}


# GET PIZZAS BY TOPPING
class Topping(BaseModel):
    name:str

@app.post("/pizzas-by-topping")
async def get_pizzas_by_topping(topping: Topping):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?pizza 
        WHERE {
            ?pizza rdfs:subClassOf+ pizza:Pizza .
            ?pizza rdfs:subClassOf [
                                    a owl:Restriction ;
                                    owl:onProperty pizza:hasTopping; 
                                    owl:someValuesFrom pizza:""" + topping.name + """ 
                        ]
        }
    """
    results = g.query(query) 

    pizzas = []
    for row in results:
        uri = row["pizza"]
        pizza = uri.split("#")[1]
        pizzas.append(pizza)
    
    return { "success": True, "payload": pizzas}

# GET PIZZAS BY COUNTRY
class Country(BaseModel):
    name:str

@app.post("/pizzas-by-country")
async def get_pizzas_by_country(country: Country):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT DISTINCT ?pizzas WHERE {
            ?pizzas rdfs:subClassOf ?restriction .
            ?restriction owl:hasValue pizza:""" + country.name + """ .
        }
    """
    results = g.query(query) 

    pizzas = []
    for row in results:
        uri = row["pizzas"]
        pizza = uri.split("#")[1]
        pizzas.append(pizza)

    return { "success": True, "payload": pizzas }


# GET TOPPINGS BY SPICINESS
class Spiciness(BaseModel):
    name:str

@app.post("/toppings-by-spiciness")
async def get_toppings_by_spiciness(spiciness:Spiciness):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT DISTINCT ?toppings WHERE {
            ?toppings rdfs:subClassOf ?restriction .
            ?restriction owl:onProperty pizza:hasSpiciness .
            ?restriction owl:someValuesFrom pizza:""" + spiciness.name + """ .
        }
    """
    results = g.query(query)

    toppings = []
    for row in results:
        uri = row["toppings"]
        topping = uri.split("#")[1]
        toppings.append(topping)

    return { "success": True, "payload": toppings }