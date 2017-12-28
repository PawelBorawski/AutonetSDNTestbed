## Autonet Testbed Server & GUI ##

### Instrukcja instalacji serwera i GUI ###

** Backend (server) **
z folderu autonet_testbed:
```
virtualenv venv
. venv/bin/activate             // Wejscie do środowiska wirtualnego Pythona
cd server/
pip install -r requirements.txt 
pip install flask_cors		// Trzeba bedzie dodac do requirements
```

Tutaj przy probie odpalenia: python run.py krzyczy ze nie ma minineta, ja to rozwiazalem tak:
```
cd ../venv/lib
git clone git://github.com/mininet/mininet
cd mininet
python setup.py install
pip install lxml
cd ../../../server
python run.py			// Powinno pojsc
```

** GUI **
z folderu autonet_testbed (po updacie):
```
. venv/bin/activate             // Wejscie do środowiska wirtualnego Pythona
pip install nodejs              // Ważne, żeby było to nie node
sudo npm install -g gulp
sudo npm install -g bower
sudo ln -s /usr/bin/nodejs /usr/bin/node  // ad. by Osin, jesli wyrzuca no such file or directory
bower install  	                // Generacja komponentów GUI
gulp dev  		        // Powinno wystartować na porcie 8888
```

Dodatki do doinstalowania w razie bledow:
```
// ad. by Osin: ja musiałem instalować bez "-g" zeby zadzialalo
sudo npm install -g gulp-connect
sudo npm install -g gulp-jshint
sudo npm install -g gulp-uglify
sudo npm install -g gulp-minify-css
sudo npm install -g gulp-clean
sudo npm install -g run-sequence
sudo npm install -g lint
```