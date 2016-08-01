<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <title>Network Function Performance Analyzer</title>

        <link href="static/css/nfpa_style.css" rel="stylesheet" type="text/css">
        <script src="static/js/nfpa.js" type="text/javascript"></script>


      <meta http-equiv="cache-control" content="max-age=0" />
      <meta http-equiv="cache-control" content="no-cache" />
      <meta http-equiv="expires" content="0" />
      <meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
      <meta http-equiv="pragma" content="no-cache" />


       
    </head>
<body>
<div class="body">
<div class="form-style-10">
% #<img src="static/note.jpg" alt="note.jpg"/>
%if config == True:
% d = data
% c = data_comment
% main_dict = {}
% main_dict_heads = {}
% user_settings = ['username']
% filesystem_settings = ['PKTGEN_ROOT', 'PKTGEN_BIN', 'MAIN_ROOT','RES_DIR',
%                        'LOG_LEVEL']
% dpdk_settings = ['cpu_core_mask', 'port_mask', 'mem_channels', 'socket_mem', 'cpu_port_assign']
% nf_settings = ['cpu_make', 'cpu_model', 'nic_make', 'nic_model', 'port_type',
%                'virtualization','vnf_name', 'vnf_version', 'vnf_driver', 
%                'vnf_driver_version', 'vnf_function', 'vnf_comment']
% gnuplot_settings = ['pps_unit', 'bps_unit', 'outlier_min_percentage',
%                     'outlier_max_percentage'] 
% traffic_settings = ['packetSizes', 'trafficTypes', 'realisticTraffics',
%                     'measurement_num', 'measurementDuration', 'sendPort', 
%                     'recvPort', 'biDir']
% #traffic_settings = [
% #                    'measurement_num', 'measurementDuration', 'sendPort', 
% #                    'recvPort', 'biDir']
% labels =  {
%              'username' : "Your username<span class='req'>*</span>",
%              'PKTGEN_ROOT' : "Pktgen's root directory<span class='req'>*</span>",
%              'PKTGEN_BIN' : "Pktgen's binary (under Pktgen's root)<span class='req'>*</span>",
%              'MAIN_ROOT' :  "NFPA's main root<span class='req'>*</span>",
%              'RES_DIR' : "Results directory (under main root)<span class='req'>*</span>",
%              'LOG_LEVEL' : "Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL (incase sensitive)<span class='req'>*</span>",
%              'cpu_core_mask' : "CPU Core Mask in HEX (e.g., e, 1f)<span class='req'>*</span>",
%              'socket_mem' : "Socket Mem option for the size of hugepages to be used (e.g., 4096)<span class='req'>*</span>",
%              'port_mask' : "Port Mask in HEX (could only be 1 or 3)<span class='req'>*</span>",
%              'mem_channels' : "Number of Hugepages to use (e.g., 4)<span class='req'>*</span>",
%              'cpu_port_assign' : "CPU Core Assignment<span class='req'>*</span>",
%              'cpu_make' : "CPU Make (e.g. intel xeon, intel atom)<span class='req'>*</span>",
%              'cpu_model' : "CPU Model (e.g. e5-2620)<span class='req'>*</span>",
%              'nic_make' : "NIC Make (e.g. intel, realtek)<span class='req'>*</span>",
%              'nic_model' : "NIC Model (e.g. xl710, 8139)<span class='req'>*</span>",
%              'port_type' : "Port Type (e.g. 10_G, 40_G)<span class='req'>*</span>",
%              'virtualization' : "Virtualization (e.g. no, docker, lxc)<span class='req'>*</span>",
%              'vnf_name' : "(Virtual) Network Function's Name (e.g. ovs, xdpd, my_own_NAT)<span class='req'>*</span>",
%              'vnf_version' : "(Virtual) Network Function's Version (e.g. 2.3.90, 0.7.5)<span class='req'>*</span>",
%              'vnf_driver' : "(Virtual) Network Function's Driver (e.g. kernel, dpdk)<span class='req'>*</span>",
%              'vnf_driver_version' : "(Virtual) Network Function's Driver's Version (e.g. 3.16, 2.0.0)<span class='req'>*</span>",
%              'vnf_function' : "(Virtual) Network Function's Function (e.g. l2-switch, l3-router, vxlan)<span class='req'>*</span>",
%              'vnf_comment' : "Comment (e.g. ivshmem + qemu version 2.3.4)<span class='req'>*</span>",
%              'pps_unit' : "Desired Unit for Packet/s (e.g., k, M, G)<span class='req'>*</span>",
%              'bps_unit' : "Desired Unit for Bit/s (e.g., k, M, G)<span class='req'>*</span>",
%              'outlier_min_percentage' : "Outliers percentage for Minimum Values (e.g., 0.05). " +\
%                                         "Use 0 to take into account all results!<span class='req'>*</span>",
%              'outlier_max_percentage' : "Outliers percentage for Maximum Values (e.g., 0.05). " +\
%                                         "Use 0 to take into account all results!<span class='req'>*</span>",
%              'packetSizes': "Packet Sizes to Use (comma separated without whitespaces, e.g., 64,128,256,1500)<span class='req'>*</span>",
%              'trafficTypes': "Synthetic Traffic Types to Use (comma separated without whitespaces, e.g., simple,tr2e,tr3i|tr3e). " + \ 
%                              "'simple' cannot be used as simple|simple! To reach this end, use Bi-directional setting. " +\
%                              "'simple|any_other' is still NOT SUPPORTED!<span class='req'>*</span>",
%              'realisticTraffics': "Realistic Traffic Types to Use (comma separated without whitespaces, e.g., wifi,mytrace,mydir1|mydir2). " +\
%                                   "Leave this field empty if not needed!",
%              'measurement_num' : "Number of measurements (e.g., 2)<span class='req'>*</span>",
%              'measurementDuration' : "Duration of one measurement in seconds (e.g., 20)<span class='req'>*</span>",
%              'sendPort' : "Send port (e.g., 0)<span class='req'>*</span>",
%              'recvPort' : "Receive port (e.g., 1)<span class='req'>*</span>",
%              'biDir' : "Bi-directional measurement (0 for simplex, 1 for duplex)<span class='req'>*</span>"
%            }
% main_dict[1] = user_settings
% main_dict_heads[1] = "User Settings"
% main_dict[2] = filesystem_settings
% main_dict_heads[2] = "Filesystem & OS Related Settings"
% main_dict[3] = dpdk_settings
% main_dict_heads[3] = "Pktgen and DPDK arguments"
% main_dict[4] = nf_settings
% main_dict_heads[4] = "Network Function Hardware & Software Related Settings"
% main_dict[5] = gnuplot_settings
% main_dict_heads[5] = "Gnuplot/Presenting Related Settings"
% main_dict[6] = traffic_settings
% main_dict_heads[6] = "Traffic Generating/PktGen Related Settings"
% list_of_values = ["packetSizes", "realisticTraffics", "trafficTypes"]


<h1>Network Function Performance Analyzer configuration
  <span>
    Set up the configuration for measurement 
      <span class="scenario_name">
        {{d['scenario_name']}}
      </span>
  </span>
  </h1>
  
<!--<img src="static/pictures/logo.png" alt="logo" style="height:100px; float:right;z-index:-3;"/>-->




% confirm_text = "Are you sure you have enabled DPDK on the interfaces you" +\
%                " want to use, and no active instance of PktGen is running?"
<br/>
<form action="/nfpa" method="post" onsubmit="return confirm('{{confirm_text}}')">
  % for i in sorted(main_dict):
    <div class="section">
      <span>
      {{i}}
      </span>
      {{main_dict_heads[i]}}
    </div>
         
      <div class="inner-wrap">
        % for j in main_dict[i]: 
          <label>
           {{!labels[j]}} 
            <div class="help">
              <span onmouseover="show_help('{{j}}_help')" 
                    onmouseout="hide_help('{{j}}_help')"/>
                    ?
              </span>
            </div>
          <div id="{{j}}_help" 
                class="note" 
                onmouseover="show_help('{{j}}_help')" 
                onmouseout="hide_help('{{j}}_help')">
            <p style="font-family: Courier; font-size:10pt;">
            % if j not in list_of_values:
              {{c[j]}}
                </p>
              </div>
               % if j == "biDir":
               % # biDir needs select field
                 % selected_simplex = ""
                 % selected_duplex = ""
                 % if str(d[j]) == "1":
                 %  selected_duplex = "selected"
                 %  selected_simplex = ""
                 % else:
                 %  selected_duplex = ""
                 %  selected_simplex = "selected"
                 % end 
                  <select name={{j}}>
                    <option value="0" {{selected_simplex}}>Simplex</option>    
                    <option value="1" {{selected_duplex}}>Duplex</option>
                  </select>
                % # pps_uni and bps_unit needs select field
                % elif j == "pps_unit" or j == "bps_unit":
                %   k = ""
                %   m = ""
                %   g = ""
                %   nothing = ""
                %   if d[j].lower() == "k":
                %     k = "selected"
                %   elif d[j].lower() == "m":
                %     m = "selected"
                %   elif d[j].lower() == "g":
                %     g = "selected"
                %   else:
                %     nothing = "selected"
                %   end
                  <select name={{j}}>
                    <option value=" " {{nothing}}>Default</option>
                    <option value="k" {{k}}>k</option>    
                    <option value="M" {{m}}>M</option>
                    <option value="G" {{g}}>G</option>
                  </select>
                % elif j == "LOG_LEVEL":
                % # LOG_LEVEL needs select field
                %   debug = ""
                %   info = ""
                %   warning = ""
                %   error = ""
                %   critical = ""
                %   if d[j].lower() == "debug":
                %     debug = "selected"
                %   elif d[j].lower() == "info":
                %     info = "selected"
                %   elif d[j].lower() == "warning":
                %     warning = "selected"
                %   elif d[j].lower() == "error":
                %     error = "selected"
                %   elif d[j].lower() == "critical":
                %     critical = "selected"
                %   end
                  <select name={{j}}>
                    <option value="DEBUG" {{debug}}>DEBUG</option>    
                    <option value="INFO" {{info}}>INFO</option>
                    <option value="WARNING" {{warning}}>WARNING</option>
                    <option value="ERROR" {{error}}>ERROR</option>
                    <option value="CRITICAL" {{critical}}>CRITICAL</option>
                  </select>
                %elif j == "port_mask":
                % # port_mask could only be 1 or 3
                %   pm_1 = ""
                %   pm_3 = ""
                %   if d[j].lower() == "1":
                %     pm_1 = "selected"
                %   elif d[j].lower() == "3":
                %     pm_3 = "selected"
                %   end
                %   # nothing is selected  
                  <select name={{j}}>
                    <option value="1" {{pm_1}}>1</option>    
                    <option value="3" {{pm_3}}>3</option>
                  </select>
                % else:
                  <input type="text" name="{{j}}" value="{{d[j]}}" />
                % end
            % else:
              % if d[j] is None:
              % string = ''
              % else:
                % num_commas = len(d[j])-1
                % n = 0
                % string = ''
                % for i in d[j]:
                %   if n < num_commas:
                %     comma = ","
                %   else:
                %     comma = ""
                %   end
                %   string += str("%s%s" % (i,comma))
                %   n += 1
                % end
              %end 
              % b = j[0:len(j)-1]
              {{c[b]}}
                </p>
                </div>
                 <input type="text" name="{{j}}" value="{{string}}" />
              %end
          </label> 
         % end         
      </div>
     
  % end 
  % # add hidden fields for non-configurable elements
    <label>
    <span class='req'>*Required field</span>
    </label>
    <input type="hidden" name="LOG_PATH" value="{{d['LOG_PATH']}}"/>
    <input type="hidden" name="scenario_name" value="{{d['scenario_name']}}"/>
    <input type="hidden" name="ETL" value="{{d['ETL']}}"/>
    <input type="hidden" name="ETL_seconds" value="{{d['ETL_seconds']}}"/>
    <input type="hidden" name="app_start_date" value="{{d['app_start_date']}}"/>
    
    <div class="button-section">
     <input type="submit" name="measure" value="Start Measurement"/>
     
     <span class="comment">NOTE: Delete SESSION COOKIES and CLEAR CACHE in your browser to avoid 
     cached contents (e.g., wrong estimated time)</span>
     <div class="footer">
       <span class="footer">{{d['version']}}
       </span>
     </div>
    </div>
    
    
</form>



%elif config == False and running == True:
% d = data
% lt = log_timestamp

<h1>Network Function Performance Analyzer
  <span>
     Measurement is running for 
      <span class="scenario_name">
        {{d['scenario_name']}}
      </span>
      <br/>
      Log file is being generated under: 
      <span class="scenario_name">
        {{d['LOG_PATH']}}log_{{lt}}.log
      </span>
  </span>
</h1>

<div class=measurement">
<p class="measurement">
DO NOT CLOSE or REFRESH this window UNTIL MEASUREMENT IS DONE!
</p>
<p class="measurement">
Progressbar is ONLY a rough estimation, the measurement may last longer.
</p>
<p class="measurement">
CHECK YOUR TERMINAL WINDOW for further status messages!

</p>
<br/><br/>
<p class="measurement">

<span> Estimated Time:
{{d['ETL']}}
</span>
</p>

<p class="measurement">
<progress id="progressBar" value="0" max="100" style="width:300px;">
</progress>
<span id="status"></span>
</p>
<p class="measurement">
<span id="finalMessage">Measuring...</span>
</p>

  <div class="footer">
    <span class="footer">{{d['version']}}
    </span>
  </div>
</div>
<script>

var tl = ({{d['ETL_seconds']}}-1)*9;
if (tl < 0)
{
  alert("INFINITE MEASUREMENT");
}
progressBarSim(0);
</script>



%elif config == False and running == False:
% d = data

<h1>Network Function Performance Analyzer
  <span>
     Measurement is DONE for 
      <span class="scenario_name">
        {{d['scenario_name']}}
      </span>
  </span>
</h1>

<div class=measurement">
<p class="measurement">
MEASUREMENT IS DONE
</p>
<p class="measurement">
Results are saved in the database on the local filesystem!
</p>
<p class="measurement">
Check {{d['MAIN_ROOT']}}/{{d['RES_DIR']}} directory, where your analyzed and plotted 
new measurements ({{d['scenario_name']}}_*.eps) and its raw data files 
({{d['scenario_name']}}_*.data) are stored.
</p>
<p class="measurement">
THANK YOU FOR USING NFPA.
</p>

<p class="measurement">
NFPA IS NOW EXITED!
</p>
</div>

%else:
  <span>No config was set</span>
  
%end
</div>
</div>

</body>
</html>
