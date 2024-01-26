mkdir /tmp/iauskour_install

curl https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz -o /tmp/iauskour_install/Python-3.10.13.tgz

tar -xvf /tmp/iauskour_install/Python-3.10.13.tgz -C /tmp/iauskour_install

(cd /tmp/iauskour_install/Python-3.10.13/ && ./configure --prefix /tmp/iauskour_install/)

(cd /tmp/iauskour_install/Python-3.10.13/ && make && make install)

/tmp/iauskour_install/bin/python3.10 -m venv venv

source venv/bin/activate

pip install -r requirements.txt


(cd llama && make simple)
