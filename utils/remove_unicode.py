from requests import get

def emojis() -> str:
    page = get("https://www.unicode.org/Public/UCD/latest/ucd/emoji/emoji-data.txt")
    lines = page.text.split("\n")

    blacklist = [ # blacklist of element who are not really emojis
        "number sign",
        "digit zero..digit nine",
        "copyright",
        "registered",
        "trade mark",
        "information"
    ]
    
    unicodes = []
    extendedEmoji = {}
    for line in lines: # check all lines
        if not line.startswith("#") and len(line) > 0: # ignores comment lines and blank lines
            if line.split(')')[1].strip() not in blacklist: # check if the emoji isn't in the blacklist
                temp = f"{line.split(';')[0]}".strip() # recovery of the first column
                if ".." in temp: # if it is a "list" of emojis, adding to a dict
                    extendedEmoji[temp.split("..")[0]] = temp.split("..")[1]
                else:
                    unicodes.append(temp)
    unicodes = list(set(unicodes) - {""}) # removal of duplicates and especially of extra spaces

    def _uChar(string: str): # choice between \u and \U in addition of the "0" to complete the code
        stringLen = len(string)
        if stringLen > 7: # Can't be more than 7 anyways
            raise Exception(f"{string} is too long! ({stringLen})")
        u, totalLong = "U", 7 # Should be 7 characters long if it is a capital U
        if stringLen < 4: # 4 characters long if smaller than 4
            u, totalLong = "u", 4 # Should be 4 characters long if it is a lowercase u
        resultat = ""
        while len(f"{resultat}{string}") <= totalLong: # Adding the 0
            resultat += "0"
        return f"\{u}{resultat}" # Return the right "U" with the right number of 0

    for i in range(0, len(unicodes)): # add unicode syntax to the list
        unicodes[i] = f"{_uChar(unicodes[i])}{unicodes[i]}"
    
    for mot in extendedEmoji.items(): # add unicode syntax to the dict
        extendedEmoji[mot[0]] = f"{_uChar(mot[1])}{mot[1]}"
        temp = f"{_uChar(mot[0])}{mot[0]}-{extendedEmoji[mot[0]]}"
        if temp not in unicodes: # if not already in the list
            unicodes.append(temp) # add the item to the list

    resultat = "["
    for code in unicodes: # conversion of the list into a string with | to separate all the emojis
        resultat += f"{code}|"

    return f"{resultat[:-1]}]+"
