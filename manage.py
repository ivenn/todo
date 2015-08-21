from app.__init__ import create_app

def start():
    app = create_app()
    #app.run(debug=True)

if __name__ == "__main__":
	start()