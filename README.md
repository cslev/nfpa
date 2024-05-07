# The great merge of NFPA and CBT 
We are delighted to announce that the [forked CBT project](https://github.com/BarrRedKola/cbt/) and NFPA has just been merged, therefore NFPA consists of all the new features (e.g., rewritten  plugin architecture to support numerous software datapaths) and scenarios the CBT guys have developed.
We joined our forces and from now the two development branches are going to improve the whole architecture under the original name and repository.
Let's keep NFPA to be the no.1 brand in open-source network function benchmarking!

# What's NEW since the great merge?
Check [ChangeLog](https://github.com/BarrRedKola/cbt/blob/master/ChangeLog) from v3.2 where the fork has been issued.

WEB interface has become OBSOLETE. We do not develop that part of CBT/NFPA further, thus new feautures we introduced
do not work with the WEB interface!

# New requirements:
gnuplot >= v5.0 (due to the utf8 encoding)




#NFPA
Network Function Performance Analyzer

It is commonly accepted that decoupling network functions (NFs) from the underlying physical 
infrastructure using virtualization and cloud technologies enables service innovation. 
Using Software Defined Networking (SDN), the programmability of the Network Function 
Virtualization (NFV) infrastructure has gained a huge potential for supporting the deployment 
of NFs in a variety of (virtualized) environments, including Internet and cloud service providers, 
campus and enterprise networks, and over-the-top applications.

Project homepage, tutorials, walkthroughs, etc.: [http://nfpa.tmit.bme.hu](http://nfpa.tmit.bme.hu)
  

One of the fundamental questions is: 
Are the software-based solutions (ever going to be) able to cope with the forever changing and increasing traffic demands? Network Function Performance Analyzer is a publicly available, open-source measurement application, which is not only following standardized methodologies (RFC 2544) but also makes it possible to comprehensively compare performance metrics of NFs in an exhaustive range of dimensions. More precisely, NFPA answers
 - how a software-based NF
 - implemented in a generic language (e.g., C/C++)
 - running on a generic platform (e.g., Intel Xeon)
 - over a generic operating system (e.g., Linux)
 - in different environments (e.g., virtual machine)
 - using different drivers performs
 - under different traffic patterns.

# Parsing NFPA trace nfo files for other purposes
Adding this tiny tidbit here as the traces are still used in many scenarios, even though NFPA is less used nowadays. 

In fact, I am using the traces with Suricata, so from the traces if I want to create a Suricata flow rule, the easiest way to do so is as follows (assuming you want to use the `nfpa.trPR_v2_48` as an example):
```
# cat nfpa.trPR_v2_48.nfo|grep -v "src_ip" |awk -F ',' '{print "alert ip "$3" "$5" -> "$4" "$6" (msg:\"nfpa_trace packet flow("$3":"$5"->"$4":"$6")\";classtype:non-suspicious;priority:1;sid:"$5$6";rev:1;)"}'
alert ip 4.183.68.159 555 -> 122.79.201.60 6312 (msg:"nfpa_trace packet flow(4.183.68.159:555->122.79.201.60:6312)";classtype:non-suspicious;priority:1;sid:5556312;rev:1;)
alert ip 174.48.34.90 45799 -> 174.10.232.131 45825 (msg:"nfpa_trace packet flow(174.48.34.90:45799->174.10.232.131:45825)";classtype:non-suspicious;priority:1;sid:4579945825;rev:1;)
alert ip 84.199.119.128 34329 -> 179.8.116.218 30057 (msg:"nfpa_trace packet flow(84.199.119.128:34329->179.8.116.218:30057)";classtype:non-suspicious;priority:1;sid:3432930057;rev:1;)
alert ip 186.22.186.101 52588 -> 160.155.123.36 63519 (msg:"nfpa_trace packet flow(186.22.186.101:52588->160.155.123.36:63519)";classtype:non-suspicious;priority:1;sid:5258863519;rev:1;)
alert ip 209.250.121.161 16736 -> 204.242.225.140 7994 (msg:"nfpa_trace packet flow(209.250.121.161:16736->204.242.225.140:7994)";classtype:non-suspicious;priority:1;sid:167367994;rev:1;)
alert ip 48.107.49.54 52700 -> 167.46.34.17 43591 (msg:"nfpa_trace packet flow(48.107.49.54:52700->167.46.34.17:43591)";classtype:non-suspicious;priority:1;sid:5270043591;rev:1;)
alert ip 218.108.213.232 24918 -> 221.10.222.7 49001 (msg:"nfpa_trace packet flow(218.108.213.232:24918->221.10.222.7:49001)";classtype:non-suspicious;priority:1;sid:2491849001;rev:1;)
alert ip 195.202.189.41 31883 -> 184.183.132.147 58242 (msg:"nfpa_trace packet flow(195.202.189.41:31883->184.183.132.147:58242)";classtype:non-suspicious;priority:1;sid:3188358242;rev:1;)
alert ip 48.131.100.17 19000 -> 160.86.52.162 38424 (msg:"nfpa_trace packet flow(48.131.100.17:19000->160.86.52.162:38424)";classtype:non-suspicious;priority:1;sid:1900038424;rev:1;)
alert ip 34.14.197.176 63022 -> 197.179.161.65 41064 (msg:"nfpa_trace packet flow(34.14.197.176:63022->197.179.161.65:41064)";classtype:non-suspicious;priority:1;sid:6302241064;rev:1;)
alert ip 78.64.126.173 52515 -> 139.172.77.82 57624 (msg:"nfpa_trace packet flow(78.64.126.173:52515->139.172.77.82:57624)";classtype:non-suspicious;priority:1;sid:5251557624;rev:1;)
alert ip 97.81.214.247 5799 -> 52.201.139.34 55377 (msg:"nfpa_trace packet flow(97.81.214.247:5799->52.201.139.34:55377)";classtype:non-suspicious;priority:1;sid:579955377;rev:1;)
alert ip 202.118.42.242 2539 -> 118.154.160.190 8836 (msg:"nfpa_trace packet flow(202.118.42.242:2539->118.154.160.190:8836)";classtype:non-suspicious;priority:1;sid:25398836;rev:1;)
alert ip 53.82.63.222 43808 -> 179.241.211.186 54023 (msg:"nfpa_trace packet flow(53.82.63.222:43808->179.241.211.186:54023)";classtype:non-suspicious;priority:1;sid:4380854023;rev:1;)
alert ip 128.91.155.8 21052 -> 178.65.222.211 39713 (msg:"nfpa_trace packet flow(128.91.155.8:21052->178.65.222.211:39713)";classtype:non-suspicious;priority:1;sid:2105239713;rev:1;)
alert ip 190.40.69.172 1075 -> 84.162.28.41 20133 (msg:"nfpa_trace packet flow(190.40.69.172:1075->84.162.28.41:20133)";classtype:non-suspicious;priority:1;sid:107520133;rev:1;)
alert ip 3.197.180.158 890 -> 31.138.168.172 2874 (msg:"nfpa_trace packet flow(3.197.180.158:890->31.138.168.172:2874)";classtype:non-suspicious;priority:1;sid:8902874;rev:1;)
alert ip 220.237.177.156 52466 -> 79.228.222.21 33660 (msg:"nfpa_trace packet flow(220.237.177.156:52466->79.228.222.21:33660)";classtype:non-suspicious;priority:1;sid:5246633660;rev:1;)
alert ip 65.176.150.51 12733 -> 92.159.102.194 18700 (msg:"nfpa_trace packet flow(65.176.150.51:12733->92.159.102.194:18700)";classtype:non-suspicious;priority:1;sid:1273318700;rev:1;)
alert ip 186.164.62.101 46825 -> 193.187.112.153 37683 (msg:"nfpa_trace packet flow(186.164.62.101:46825->193.187.112.153:37683)";classtype:non-suspicious;priority:1;sid:4682537683;rev:1;)
alert ip 103.182.235.40 57135 -> 45.188.5.79 44900 (msg:"nfpa_trace packet flow(103.182.235.40:57135->45.188.5.79:44900)";classtype:non-suspicious;priority:1;sid:5713544900;rev:1;)
alert ip 147.35.159.138 21226 -> 198.213.199.132 60807 (msg:"nfpa_trace packet flow(147.35.159.138:21226->198.213.199.132:60807)";classtype:non-suspicious;priority:1;sid:2122660807;rev:1;)
alert ip 63.97.19.74 7950 -> 48.61.60.103 53739 (msg:"nfpa_trace packet flow(63.97.19.74:7950->48.61.60.103:53739)";classtype:non-suspicious;priority:1;sid:795053739;rev:1;)
alert ip 27.134.104.175 41142 -> 141.120.204.34 53587 (msg:"nfpa_trace packet flow(27.134.104.175:41142->141.120.204.34:53587)";classtype:non-suspicious;priority:1;sid:4114253587;rev:1;)
alert ip 73.241.15.248 11279 -> 84.167.231.116 51642 (msg:"nfpa_trace packet flow(73.241.15.248:11279->84.167.231.116:51642)";classtype:non-suspicious;priority:1;sid:1127951642;rev:1;)
alert ip 191.243.137.132 4958 -> 16.107.150.84 41337 (msg:"nfpa_trace packet flow(191.243.137.132:4958->16.107.150.84:41337)";classtype:non-suspicious;priority:1;sid:495841337;rev:1;)
alert ip 205.134.144.64 11796 -> 183.14.60.85 3238 (msg:"nfpa_trace packet flow(205.134.144.64:11796->183.14.60.85:3238)";classtype:non-suspicious;priority:1;sid:117963238;rev:1;)
alert ip 81.68.208.212 2235 -> 68.115.46.134 46997 (msg:"nfpa_trace packet flow(81.68.208.212:2235->68.115.46.134:46997)";classtype:non-suspicious;priority:1;sid:223546997;rev:1;)
alert ip 211.82.107.253 42800 -> 31.37.91.102 18690 (msg:"nfpa_trace packet flow(211.82.107.253:42800->31.37.91.102:18690)";classtype:non-suspicious;priority:1;sid:4280018690;rev:1;)
alert ip 159.2.211.109 2489 -> 140.202.173.157 19217 (msg:"nfpa_trace packet flow(159.2.211.109:2489->140.202.173.157:19217)";classtype:non-suspicious;priority:1;sid:248919217;rev:1;)
alert ip 6.2.82.59 49556 -> 113.110.154.47 43002 (msg:"nfpa_trace packet flow(6.2.82.59:49556->113.110.154.47:43002)";classtype:non-suspicious;priority:1;sid:4955643002;rev:1;)
alert ip 15.212.199.188 55125 -> 64.219.91.126 25650 (msg:"nfpa_trace packet flow(15.212.199.188:55125->64.219.91.126:25650)";classtype:non-suspicious;priority:1;sid:5512525650;rev:1;)
alert ip 135.121.174.163 27061 -> 89.173.89.82 43880 (msg:"nfpa_trace packet flow(135.121.174.163:27061->89.173.89.82:43880)";classtype:non-suspicious;priority:1;sid:2706143880;rev:1;)
alert ip 114.95.90.129 29036 -> 160.74.253.175 51307 (msg:"nfpa_trace packet flow(114.95.90.129:29036->160.74.253.175:51307)";classtype:non-suspicious;priority:1;sid:2903651307;rev:1;)
alert ip 54.19.240.153 48384 -> 146.240.110.149 22308 (msg:"nfpa_trace packet flow(54.19.240.153:48384->146.240.110.149:22308)";classtype:non-suspicious;priority:1;sid:4838422308;rev:1;)
alert ip 14.174.172.216 19310 -> 96.72.95.191 32377 (msg:"nfpa_trace packet flow(14.174.172.216:19310->96.72.95.191:32377)";classtype:non-suspicious;priority:1;sid:1931032377;rev:1;)
alert ip 143.218.209.15 33008 -> 107.193.217.89 16682 (msg:"nfpa_trace packet flow(143.218.209.15:33008->107.193.217.89:16682)";classtype:non-suspicious;priority:1;sid:3300816682;rev:1;)
alert ip 41.93.74.16 45945 -> 158.255.251.28 11839 (msg:"nfpa_trace packet flow(41.93.74.16:45945->158.255.251.28:11839)";classtype:non-suspicious;priority:1;sid:4594511839;rev:1;)
alert ip 165.124.135.242 2698 -> 145.128.201.100 12449 (msg:"nfpa_trace packet flow(165.124.135.242:2698->145.128.201.100:12449)";classtype:non-suspicious;priority:1;sid:269812449;rev:1;)
alert ip 139.115.87.75 13096 -> 94.27.132.241 57729 (msg:"nfpa_trace packet flow(139.115.87.75:13096->94.27.132.241:57729)";classtype:non-suspicious;priority:1;sid:1309657729;rev:1;)
alert ip 190.89.127.25 57775 -> 32.245.108.68 31216 (msg:"nfpa_trace packet flow(190.89.127.25:57775->32.245.108.68:31216)";classtype:non-suspicious;priority:1;sid:5777531216;rev:1;)
alert ip 190.131.163.175 61293 -> 88.113.224.138 44118 (msg:"nfpa_trace packet flow(190.131.163.175:61293->88.113.224.138:44118)";classtype:non-suspicious;priority:1;sid:6129344118;rev:1;)
alert ip 138.88.236.87 41249 -> 154.93.220.221 45821 (msg:"nfpa_trace packet flow(138.88.236.87:41249->154.93.220.221:45821)";classtype:non-suspicious;priority:1;sid:4124945821;rev:1;)
alert ip 64.30.89.201 9623 -> 202.238.147.61 26457 (msg:"nfpa_trace packet flow(64.30.89.201:9623->202.238.147.61:26457)";classtype:non-suspicious;priority:1;sid:962326457;rev:1;)
alert ip 35.251.83.39 14770 -> 93.227.249.77 15840 (msg:"nfpa_trace packet flow(35.251.83.39:14770->93.227.249.77:15840)";classtype:non-suspicious;priority:1;sid:1477015840;rev:1;)
alert ip 101.104.97.210 7987 -> 141.105.80.189 58020 (msg:"nfpa_trace packet flow(101.104.97.210:7987->141.105.80.189:58020)";classtype:non-suspicious;priority:1;sid:798758020;rev:1;)
alert ip 201.138.94.247 42097 -> 48.181.42.68 42366 (msg:"nfpa_trace packet flow(201.138.94.247:42097->48.181.42.68:42366)";classtype:non-suspicious;priority:1;sid:4209742366;rev:1;)
alert ip 112.194.243.253 6066 -> 87.169.247.85 39936 (msg:"nfpa_trace packet flow(112.194.243.253:6066->87.169.247.85:39936)";classtype:non-suspicious;priority:1;sid:606639936;rev:1;)
```

Feel free to modify the `awk` print statement according to your needs. 

