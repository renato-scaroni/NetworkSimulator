Host criado  h0
Host criado  h1
Host criado  h2
Host criado  h3
Router criado  r0
Router criado  r1

h0 :
ip 10.0.0.1
router 10.0.0.2
DNS: 192.168.1.1 


h1 :
ip 10.1.1.1
router 10.1.1.2
DNS: 192.168.1.1 


h2 :
ip 192.168.2.2
router 192.168.2.3
DNS: 192.168.1.1 


h3 :
ip 192.168.1.1
router 192.168.1.2
DNS: 1.1.1.1 


r0 :
orig 10.0.0.2
dest 0 

orig 10.1.1.2
dest 1 

orig 192.168.3.3
dest 2 


r1 :
orig 192.168.3.4
dest 0 

orig 192.168.2.3
dest 1 

orig 192.168.1.2
dest 2 

config de rota para r0
orig 10.0.0.0
dest 0 

orig 10.1.1.0
dest 1 

orig 192.168.3.0
dest 2 

orig 192.168.2.0
dest 192.168.3.4 

orig 192.168.1.0
dest 192.168.3.4 

config de rota para r1
orig 192.168.3.0
dest 0 

orig 192.168.2.0
dest 1 

orig 192.168.1.0
dest 2 

orig 10.0.0.0
dest 192.168.3.3 

orig 10.1.1.0
dest 192.168.3.3 

config de perforance para r0
Tempo de processamento de pacotes 100
porta 0
limite 1000 

porta 1
limite 1000 

porta 2
limite 1000 

config de perforance para r1
Tempo de processamento de pacotes 20
porta 0
limite 1000 

porta 1
limite 1000 

porta 2
limite 1000 

Http Server criado  httpc0
Http Server criado  httpc1
Http Client criado  https2
DNS Server criado  dns3
httpc0 associado a h0
httpc1 associado a h1
https2 associado a h2
dns3 associado a h3
sniffer criado  sniffer1
sniffer criado  sniffer2
sniffer no link para r1.0
sniffer no link para r0.2
sniffer no link para r0.1
sniffer no link para h1
commands to execute :
(0.5, '"httpc0 GET h2"')
(0.6, '"httpc1 GET h0"')
(0.6, '"httpc1 GET 192.168.2.2"')
(0.7, '"httpc0 GET h2"')
(4.0, '"finish"')
CLOCK 0
Comando: "finish"
executando router  r0
r0.0 --> h0 10ms 10Mbps
r0.1 --> h1 2ms 5Mbps
r0.2 --> r1.0 20ms 2Mbps
executando router  r1
r1.0 --> r0.2 20ms 2Mbps
r1.1 --> h2 5ms 10Mbps
r1.2 --> h3 2ms 5Mbps
executando host  h2
h2 --> r1.1 5ms 10Mbps
executando host  h3
h3 --> r1.2 2ms 5Mbps
executando host  h0
h0 --> r0.0 10ms 10Mbps
executando host  h1
h1 --> r0.1 2ms 5Mbps
