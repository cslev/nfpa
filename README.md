#We are delighted to announce that the forked CBT project and NFPA has just been merged, therefore NFPA consists of all the new features (e.g., rewritten  plugin architecture to support numerous software datapaths) and scenarios the CBT guys have developed.
We joined our forces and from now the two development branches are going to improve the whole architecture under the original name.
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
By means of Software Defined Networking (SDN), the programmability of the Network Function 
Virtualization (NFV) infrastructure has gained a huge potential for supporting the deployment 
of NFs in a variety of (virtualized) environments, including Internet and cloud service providers, 
campus and enterprise networks, and over-the-top applications.

Project homepage, tutorials, walkthroughs, etc.: [http://nfpa.tmit.bme.hu](http://nfpa.tmit.bme.hu)
  

One of the fundamental questions is: 
Are the software-based solutions (ever going to be) able to cope with the forever changing and increasing traffic demands? Network Function Performance Analyzer is a publicly available, open-source measurement application, which is not only in accordance with standardized methodologies (RFC 2544), but also makes possible to comprehensively compare performance metrics of NFs in an exhaustive range of dimensions. More precisely, NFPA answers
 - how a software-based NF
 - implemented in a generic language (e.g., C/C++)
 - running on a generic platform (e.g., Intel Xeon)
 - over a generic operating system (e.g., Linux)
 - in different environments (e.g., virtual machine)
 - using different drivers performs
 - under different traffic patterns.



