package.path = package.path ..";?.lua;test/?.lua;app/?.lua;"


require "Pktgen";



-- ################### CONFIGURATION PART ########################

-- for config params read from the config file

-- local variables for config parameters (read from config.cfg)
config = {};
-- local variable for different packet sizes (read from config.cfg)
pktSizes = {};


-- setting sending rate to 100% at the beginning
sending_rate=100;
scale_factor=sending_rate;
last_sending_rate=sending_rate;




-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function read_config_file ()

  print("Reading the config file... (nfpa.cfg)\n");

  -- Opens a file in read
  config_file = io.open("nfpa.cfg", "r");

  -- sets the default input file as test.lua
  io.input(config_file);

  print("Read config params:\n");
  -- loop over all lines in the config file
  for line in io.lines()
  do
    -- omit commented lines (check the first letter whether it is '#')
    -- and also omit empty lines
    if not (string.sub(line,0,1)=="#") and (line ~= "")
    then
      -- tokenize and put the config params into a dictionary
      -- first, find equal sign position
      -- string.find only matches the first equal sign, so we do not need
      -- to worry about it and/or escaping further equal signs as special chars
      local equal_pos = string.find(line,"=");
      -- accordingly, key will be the substring before equal sign
      key = string.sub(line,0,equal_pos-1);
      -- and value will be the substring after equal sign
      value = string.sub(line,equal_pos+1);
        -- packetSize fields found
      if(key == "packetSize")
      then
        -- store desired packet sizes
        table.insert(pktSizes, value);
      end
      -- store other config parameters in config var
      -- such as measureDuration, sendPort, recvPort, etc.
      config[key] = value;


      if key == "biDir"
      then
        print(key,"\t\t",value);
      else
        print(key,"\t",value);
      end
      
    else
     -- nothing to do, these lines are comments <-- Lua has no continue
     -- statement. That's why this check is done likewise
    end
  end

  -- closes the opened file
  io.close(config_file);
  
end
-- ====================== END FUNCTION ========================

function parse_config ()
  -- determine port rate
  print("Parsing configuration file...");  
  
  -- check for special ul-dl birdirectional traffic
  for key,value in pairs(config)
  do
    if key == "trafficType"
    then
      pipe_sign = string.find(value,"|");
      if pipe_sign ~= nil
      then
        t1 = string.sub(value,0,pipe_sign-1);
        t2 = string.sub(value,pipe_sign+1);
        print("2 traffic files for the two ports: " .. t1 .. " and " .. t2 ..
              "\n");
        -- update biDir accordingly
        config["biDir"] = 1;
        print("Update: biDir=1");
      end
    end
    
  end    
    
end

-- ################### END CONFIGURATION ######################



-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
-- Output file check
-- file_name string - output filename check to
function file_check (file_name)
  file_found = io.open(file_name, "r");
  
  if file_found==nil
  then
    print(file_name .. " does not exists. Write initial head data " ..
          "into the file\n");
   
    return true;
  else
    print(file_name .. " exists so unecessary data will not be written again\n");
    return false;
  end
end
-- ====================== END FUNCTION ========================




-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function measure2 ()
  -- increase measure counter
  measure2_called = measure2_called + 1;

  sent_avg=0;
  recv_avg=0;
  
  -- measure time in seconds (i.e., the seconds a measurement with a 
  -- certain sending_rate lasts
  measure_time=3;
  
  -- kind of a warm up for the changed sending_rate
  print("Tuning in with sending rate ".. sending_rate_1 .."% for 3 secs" 
        .. "on port" .. config["sendPort"] .. "\n");
  
  -- check whether bidirectional scenario is set up
  if(tonumber(config["biDir"]) == 1)
  then
    print("Tuning in with sending rate ".. sending_rate_2 .."% for 3 secs" 
        .. "on port" .. config["recvPort"] .. "\n");
    -- create send/recv avg variables for the other direction as well
    sent_avg_2=0;
    recv_avg_2=0;
  end
  sleep(3);
  
  print("Tuned in! -> Measure");
  for i=1,measure_time
  do
    -- get port data
    portRates = pktgen.portStats("all", "rate");
    -- get sent packet/s data
    sent_pkts = portRates[tonumber(config["sendPort"])].pkts_tx;
    -- calculate sending throughput in mbps
    sent_bps = math.floor(sent_pkts*(config["packetSize"]+20)*8);
    -- get received packet/s data
    recv_pkts = portRates[tonumber(config["recvPort"])].pkts_rx;
    -- calculate receiving throughput in mbps    
    recv_bps = math.floor(recv_pkts*(config["packetSize"]+20)*8);
    

    -- calculate the number of missing packets
    miss_pkts = sent_pkts - recv_pkts;
    -- calculate the difference between sent and received mbit/s
    diff_bps = sent_bps - recv_bps;
  
    

    -- log data into file
    -- prettify output
    io.write(sent_pkts .. "|" .. recv_pkts ..  "|".. miss_pkts .. "|" .. 
             sent_bps ..  "|" .. recv_bps .. "|" .. diff_bps);


    sent_avg=sent_avg + sent_pkts;
    recv_avg=recv_avg + recv_pkts;
    
    -- capture bidirectional traffic as well if biDir was set
    if tonumber(config["biDir"]) == 1
    then
      -- get sent packet/s data
      sent_pkts2 = portRates[tonumber(config["recvPort"])].pkts_tx;
      -- calculate sending throughput in mbps
      sent_bps2 = math.floor(sent_pkts2*(config["packetSize"]+20)*8);
      -- get received packet/s data
      recv_pkts2 = portRates[tonumber(config["sendPort"])].pkts_rx;
      -- calculate receiving throughput in mbps
      recv_bps2 = math.floor(recv_pkts2*(config["packetSize"]+20)*8);
      -- calculate the number of missing packets
      miss_pkts2 = sent_pkts2 - recv_pkts2;
      -- calculate the difference between sent and received mbit/s
      diff_bps2 = sent_bps2 - recv_bps2;
      -- log data into file
      -- prettify output
      io.write("|" .. sent_pkts2 .. "|" .. recv_pkts2 ..  "|".. miss_pkts2
              .. "|" .. sent_bps2 ..  "|" .. recv_bps2 .. "|" .. diff_bps2);

      send_avg_2 = sent_avg_2 + sent_pkts2;
      recv_avg_2 = recv_avg_2 + recv_pkts2;

    end

                     
               
    io.write("\n");
          
    -- practically write out each line into the file in each seconds
    -- instead of only writing the results when measurement is done
    io.flush();
    
    sleep(1);
  end
  
  -- calculate averages according to the seconds one measurement lasted
  sent_avg=math.floor(sent_avg/measure_time);
  recv_avg=math.floor(recv_avg/measure_time);
  
  
  -- bidirectional case
  if(tonumber(config["biDir"]) == 1)
  then
    sent_avg_2 = math.floor(sent_avg_2/measure_time);
    recv_avg_2 = math.floor(recv_avg_2/measure_time);
  end
  
  if measure2_called > 3
  then
    --check recv values to see whether VNF was configured properly
    if recv_avg == 0
    then
      print("There is not packets received on port " .. 
            config["recvPort"] .. "! - EXITING...");
      os.exit(-2);
      -- TODO: Main app should handle this differently!
    end
    
    if tonumber(config["biDir"]) == 1 and recv_avg_2 == 0
    then
      print("There is not packets received on port " .. 
            config["sendPort"] .. "! - EXITING...");
      os.exit(-2);
      -- TODO: Main app should handle this differently!
    end
  
  end
  
end
-- ====================== END FUNCTION ========================

-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function change_rate (port, exact, increase)
-- adjusting rates for port - if exact is -1, reducing always by the
-- base factor, otherwise rate is set to the value of exact

  last_sending_rate = sending_rate;

  if exact == -1
  then
    -- sometimes the rate only changes below 10%. In this case, we just
    -- step down until 1% (sadly, float numbers are not supported)
    scale_factor=math.floor(scale_factor/2);
    if increase == false
    then
      sending_rate = sending_rate - scale_factor;
    else
      sending_rate = sending_rate + scale_factor;
    end
  else
    sending_rate = exact;
  end
  -- changing the sending rate
  pktgen.set(port,"rate", sending_rate);

end
-- ====================== END FUNCTION ========================




-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function tune_in ()
  sent_avg=0;
  recv_avg=0;
  print("Tuning in with sending rate ".. sending_rate .."% for 3 secs...");
  sleep(3);

  print("Measure");
  for i=1,3
  do
    -- get port data
    portRates = pktgen.portStats("all", "rate");
    -- get sent packet/s data
    sent_pkts = portRates[tonumber(config["sendPort"])].pkts_tx;
    -- get received packet/s data
    recv_pkts = portRates[tonumber(config["recvPort"])].pkts_rx;

    sent_avg=sent_avg + sent_pkts;
    recv_avg=recv_avg + recv_pkts;
    sleep(1);
  end

  sent_avg=math.floor(sent_avg/3);
  recv_avg=math.floor(recv_avg/3);

end
-- ====================== END FUNCTION ========================


-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++
function measure ()
  print("Best sending rate is " .. sending_rate .. "%!");
  -- further warmup with the final sending_rate
  sleep(3);
  for i=1,3
  do
    -- get port data
    portRates = pktgen.portStats("all", "rate");
    -- get sent packet/s data
    sent_pkts = portRates[tonumber(config["sendPort"])].pkts_tx;
    -- calculate sending throughput in mbps
    sent_bps = math.floor(sent_pkts*(config["packetSize"]+20)*8);
    -- get received packet/s data
    recv_pkts = portRates[tonumber(config["recvPort"])].pkts_rx;
    -- calculate receiving throughput in mbps
    recv_bps = math.floor(recv_pkts*(config["packetSize"]+20)*8);
    -- calculate the number of missing packets
    miss_pkts = sent_pkts - recv_pkts;
    -- calculate the difference between sent and received mbit/s
    diff_bps = sent_bps - recv_bps;

  -- log data into file
    -- prettify output
    io.write(sent_pkts .. "|" .. recv_pkts ..  "|".. miss_pkts .. "|" ..
             sent_bps ..  "|" .. recv_bps .. "|" .. diff_bps);


    print("Send\tRecv");
    print(sent_pkts .. "\t" .. recv_pkts);
    sleep(1);
  end
end
-- ====================== END FUNCTION ========================

-- +++++++++++++++++++++++++ FUNCTION ++++++++++++++++++++++++++++

function start_measurement ()
  
  traffic = config["trafficType"] .. "." .. config["packetSize"];
  -- get the number of desired packet sizes used for measurement
  number_of_packetsizes = #pktSizes;
  -- calculating estimated measurement duration
  -- heating up=3s, cooldown=3s, config["measurementDuration"], number_of_packetsizes
  estimated_time = " less than a minute!"
  if tonumber(config["measurementDuration"]) ~= 0
  then
    infinite_measurement = false;
  else
    estimated_time = "INFINITE"
    infinite_measurement = true;
  end
  
  print("Estimated time needed for this traffic trace is: " .. estimated_time);

  pktgen.set(tonumber(config["sendPort"]),"rate", sending_rate);
  pktgen.start(tonumber(config["sendPort"]));

  -- wait some seconds to avoid slow start
  print("Waiting for heating up\n");
  sleep(3);

  
  tune_in();

  error_rate = 0.01

  sending_rate_found = false

  while not sending_rate_found
  do

    miss_pkts = sent_avg - recv_avg;
    threshold = sent_avg*error_rate;


    print("\nSent:" .. sent_avg);
    print("Recv:" .. recv_avg);
    print("Miss:" .. miss_pkts);

    print("Threshold:" .. threshold);
    --~ print("Sending rate: " .. sending_rate);

    -- if sending_rate is altering among 2 values that are next to each
    -- other, we quit!
    if math.abs(sending_rate - last_sending_rate) == 1
    then
      print("We reached a possibly good sending rate");
      sending_rate=sending_rate+1; -- increase sending rate the greater value
      change_rate(tonumber(config["sendPort"]),sending_rate,false);
      sending_rate_found = true
      measure();
    else

      -- check threshold
      if threshold < miss_pkts
      then
        -- recv and sent are still too far from each other
        print("Threshold not reached!");
        change_rate(tonumber(config["sendPort"]),-1,false);
        tune_in();

      else
        -- threshold reached - we may jumped to much, check greater rate
        print("Threshold meet...");
        if sending_rate > 99
        then
          print("Best sending rate was 100%...measuring this rate...");
          sending_rate_found = true;
          measure();
        else
          change_rate(tonumber(config["sendPort"]),-1,true);
          tune_in();
        end
      end
    end
  end
end
-- ====================== END FUNCTION ========================






-- ##################### MAIN ###################
-- reset everything
-- clear pktgen's current stats
pktgen.clear("all");
pktgen.cls();
pktgen.screen("off");
sleep(1);
pktgen.screen("on");

-- read the config
read_config_file();
-- parsing config and check every variable is set correctly
parse_config();




-- Start measurement
-- RESULTS WILL BE WRITTEN TO OUTPUT FILES
start_measurement();

print("Exiting...");
-- switching screen off, since w/o this exiting pktgen influences the terminal
-- and only the half of it can be used!
pktgen.screen("off");

sleep(1);
-- pktgen.quit();
os.exit();



