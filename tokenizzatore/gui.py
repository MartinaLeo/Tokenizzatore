import tkinter as tk
from tokenizzatore import tokenizza

class Interfaccia:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('550x125')
        self.root.title('Tokenizzatore')

        # label
        self.label = tk.Label(self.root)
        self.label.config(text='Inserisci frase da tokenizzare')

        # botton
        self.btn1 = tk.Button(self.root, text='Tokenizza', width=25, padx=5, pady=15)

        # entry
        self.entry = tk.Entry(self.root, width=50)
        self.entry.insert(0, 0)
        self.contents = tk.IntVar()
        self.contents.set('')
        self.entry['textvariable'] = self.contents

        # packing
        self.label.pack(fill=tk.BOTH)
        self.entry.pack(fill=tk.BOTH)
        self.btn1.pack(fill=tk.X)

        # binding evento
        self.btn1.bind('<Button-1>', self.tokenizza)
        self.btn1.bind('<Key>', self.tokenizza)

        # stringa da tokenizzare, elementi da non normalizzare
        self.text_entry = ''
        self.to_capitalize = list()

        self.root.mainloop()

    def tokenizza(self, event):
        self.text_entry = self.entry.get()

        self.label.config(text='Inserisci, se presenti, termini da non normalizzare (separati da spazio)')
        self.contents.set('')

        self.btn2 = tk.Button(text='Inserisci', command=lambda: self.inserisci_path(normalizza=True), width=25, padx=5, pady=15)
        self.btn3 = tk.Button(text='Normalizza tutto', command=self.inserisci_path, width=25, padx=5, pady=15)

        event.widget.pack_forget()
        self.btn2.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.btn3.pack(fill=tk.X, side=tk.RIGHT, expand=True)

    def inserisci_path(self, normalizza=False):
        if normalizza:
            tmp = self.entry.get().split()
            for word in tmp:
                word = word.capitalize()
                self.to_capitalize.append(word)

        self.contents.set('')
        self.label.config(text="Inserisci il path dove memorizzare l'output")
        self.btn4 = tk.Button(self.root, text='Inserisci', command=self.avvia_tokenizzazione, width=25, padx=5, pady=15)

        self.btn2.pack_forget()
        self.btn3.pack_forget()
        self.btn4.pack(fill=tk.X)

    def avvia_tokenizzazione(self):
        path = self.entry.get().rstrip()
        try:
            last_index = path.rindex('/')
        except ValueError:
            testo = 'Path non valido. Inserisci path come /Users/myUsername/Desktop/myFolder'
            self.label.config(text=testo)
        else:
            self.contents.set('')
            nome_folder = path[last_index + 1:]
            tokenizza(self.text_entry, path, non_normalizzare=self.to_capitalize)
            testo = f"Tokenizzazione completata con successo. " \
                    f"Tokenizzazione memorizzata nel file {nome_folder} \n\nPATH:{path}"
            self.label.config(text=testo)

            self.btn5 = tk.Button(self.root, text='Esci', command=self.root.quit, width=25, padx=5, pady=15)

            self.btn4.pack_forget()
            self.btn5.pack(fill=tk.BOTH)