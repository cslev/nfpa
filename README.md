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
We will use the `src_port` and `dst_port` and add them to `1000000` to have a proper unique `sid` for each rule that is above 1M and below 2M, hence the `{sum=1000000+$5+$6}` in the beginning of the `awk` parameters.
```
# cat nfpa.trPR_v2_48.nfo|grep -v "src_ip" |awk -F ',' '{sum=1000000+$5+$6} {print "alert ip "$3" "$5" -> "$4" "$6" (msg:\"nfpa_trace packet flow("$3":"$5"->"$4":"$6")\";classtype:not-suspicious;priority:1;sid:"sum";rev:1;)"}'

```

Feel free to modify the `awk` print statement according to your needs. 

