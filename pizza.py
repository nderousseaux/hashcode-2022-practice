import numpy as np
import os
from random import randint

source_path = "./input"
res_path = "./outputGen"
nb_pizzas = 1000

"""
    return :
        ingredients[ingredient]
            Liste des ingrédients
        like[client, ingredient]
            Liste des aliments aimés par chaque client
        dont_like[client, ingredient]
            Liste des aliments non aimés par chaque client
"""
def open_file(file_path):
    print("Ouverture de : {}".format(file_path))
    

    with open(file_path, "r") as file:
        nb_clients = int(file.readline())

        ingredients = []
        clients = []
        
        zeroLine = np.full((nb_clients,1), 0)

        for i in range(nb_clients):
            c = {"like": [], "dont_like": []}
            clients.append(c)

            data = file.readline().split()
            for ing in data[1:]:
                if ing not in ingredients: ingredients.append(ing)
                c["like"].append(ingredients.index(ing))

            data = file.readline().split()
            for ing in data[1:]:
                if ing not in ingredients: ingredients.append(ing)
                c["dont_like"].append(ingredients.index(ing))
    
    like = np.full((nb_clients,len(ingredients)), 0)
    dont_like = np.full((nb_clients,len(ingredients)), 0)
        
    for i in range(len(clients)):
        like[i,:] = [1 if ingredient in clients[i]["like"] else 0 for ingredient in range(len(ingredients))]
        dont_like[i,:] = [1 if ingredient in clients[i]["dont_like"] else 0 for ingredient in range(len(ingredients))]
        
    print("Fin de l'import des données de : {}".format(file_path))
    return ingredients, like, dont_like

def save_file(file_path, ingredients, note):
    with open(file_path, "w") as file:
        file.write(str(len(ingredients)))
        for ing in ingredients:
            file.write(' '+ing)
        file.write('\n' +str(note))


"""
    return :
        note
            Note de la pizza
"""
def note(pizza, like, dont_like):
    
    nb_like_total = np.sum(like,axis=1) #[client] : Nombre d'aliment aimé par chaque client
    nb_like = np.dot(pizza,like.T) #[client] : Nombre d'aliments aimé dans la pizza
    client_like = np.equal(nb_like,nb_like_total) #[client] : True si le client à tout ses ingrédients aimé dans la pizza

    nb_dont_like = client_dont_like = np.dot(pizza,dont_like.T) #[client] : Nombre d'aliment pas aimé dans la pizza
    client_dont_like = (nb_dont_like==0) #[client] : True si le client n'a aucun de ses ingrédients détesté dans la pizza

    apprecie = client_like.astype(int)*client_dont_like.astype(int) #[client] : 1 si le client apprécie la pizza
    

    return np.sum(apprecie)


"""
    return :
        menus_max[pizza, ingredients]
            100 meilleures recettes
        notes_max[pizza]
            Note de chaque recette
"""
def best_pizzas(menus, like, dont_like):

    notes = np.apply_along_axis(note, 1, menus, like, dont_like)
    index_max = (-notes).argsort()[:nb_pizzas//100]

    notes_max = notes[index_max]
    menus_max = menus[index_max]

    return menus_max, notes_max

"""
    return:
        menus[pizza, ingredients]:
"""
def reproduction(menus):
    nb_reprod = 99

    menus = np.repeat(menus, nb_reprod, axis=0)

    #Nombre de modification pour chaque recette
    nb_modifs = np.random.chisquare(3, len(menus))
    nb_modifs = np.around((nb_modifs/np.max(nb_modifs))*menus.shape[1])
    for i in range(0, len(menus)):
        if i % nb_reprod == 0: continue #On garde la recette originale

        #On modifie aléatoirement un certain nombre d'ingrédients
        for j in [randint(0, menus.shape[1]-1) for k in range(int(nb_modifs[i]))]:
            if menus[i,j] == 0: menus[i,j] = 1
            else: menus[i,j] = 0

    #On crée 1% pizzas vraiment nouvelles   
    menus = np.concatenate((
        menus,
        np.random.randint(low=0,high=2,size=(nb_pizzas//100,len(ingredients)))
    ))

    return menus


if __name__ == "__main__":

    #Pour chaque fichier
    for file in sorted(os.listdir(source_path)):

        #On récupère les données
        ingredients, like, dont_like = open_file(os.path.join(source_path,file))

        #On crée 1 000 pizzas différentes
        #(pizza, ingredient)
        pizzas = np.random.randint(low=0,high=2,size=(nb_pizzas,len(ingredients)))
        
        #On garde les 100 meilleures
        pizzas, notes = best_pizzas(pizzas, like, dont_like)

        best_pizza = pizzas[0,]
        note_best_pizza = notes[0]

        i = 0
        while i<20:
            #On fait "se reproduire" les pizzas 
            pizzas = reproduction(pizzas)
            #On garde les 1% meilleures
            pizzas, notes = best_pizzas(pizzas, like, dont_like)

            print("{}, {}".format(notes[0], note_best_pizza))
            
            #On enregistre LA meilleure, si elle est mieux
            if(notes[0]>note_best_pizza):
                best_pizza = pizzas[0,]
                note_best_pizza = notes[0]
                i=0
            else:
                i+=1


        ingredients_best = [ingredients[i] for i in range(len(ingredients)) if best_pizza[i]==1]
        
        save_file(os.path.join(res_path, file), ingredients_best, note_best_pizza)