# DNA extraction protocol fot the OT-2 robot. 
'''
The v4.5 version uses smaller volumes to avoid pipetting twice the same liquid. 
The "liquid-cap" during chloroform dispensing is also implemented to get rid of filtered tips.
'''

# see this link to have a visual upport of plate positions and all the relevant steps of this protocol
# https://docs.google.com/presentation/d/1JAKohkoa89mKwnr0rshk1j7QGQOGtWpTiSLGF0zlCcg/edit#slide=id.g1f2df41ff5d_0_17

############################################################
# Enter your values at lines 11 to 18
############################################################
first_column_plate_1 = 1
last_column_plate_1  = 10
first_column_plate_2 = 1
last_column_plate_2  = 7
first_column_plate_3 = 0
last_column_plate_3  = 0
first_column_plate_4 = 0
last_column_plate_4  = 0

tipsbox = 'vwrnonfiltered_96_tiprack_300ul'             # tipsbox or 'vwrbox_96_tiprack_300ul' or 'vwrnonfiltered_96_tiprack_300ul' ...
samples_plate_type = '1.2ml_simport_vwr_t1102_96well'   # Enter the API name for the plates in which the samples were collected ('3axygen96wellminitubesystemcorning_96_wellplate_1320ul' OR '1.2ml_simport_vwr_t1102_96well' )
elution_buffer_volume = 30                              # Set the volume of Elution buffer (EB buffer) that will be used to resuspend yor DNA after isolation
reservoir_type = 'axygen_1_reservoir_300000ul'

###########################################################
# Leave as it is the rest of the script
###########################################################

# Running the Opentrons API
from opentrons import protocol_api
from opentrons import types
import math
import time

metadata = {'protocolName': 'DNA extraction protocol v4.5 -- MiniVols --', 'apiLevel': '2.15'}

def get_values(*names):
    import json
    _all_values = json.loads("""{}""")
    return [_all_values[n] for n in names]

# Defining variables
string1 = " ------------ "
string2 = "The next step will be done in "
string3 = " minutes."
buffer_volume = 280         
distance_interstice_to_bottom = 0               # To obtain this value, add the quantity of chloroform to an empty tube of the starting samples plates and measure the heigth of the liquid from the botom of the tube.
if samples_plate_type == '3axygen96wellminitubesystemcorning_96_wellplate_1320ul': distance_interstice_to_bottom = 16
if samples_plate_type == '1.2ml_simport_vwr_t1102_96well' : distance_interstice_to_bottom = 14


# Defining the total number of columns with samples in each plates
if first_column_plate_1 == 0 : number_of_columns_plate_1 = 0 
else: number_of_columns_plate_1 = (last_column_plate_1-first_column_plate_1 + 1)
if first_column_plate_2 == 0 : number_of_columns_plate_2 = 0 
else: number_of_columns_plate_2 = (last_column_plate_2-first_column_plate_2 + 1)
if first_column_plate_3 == 0 : number_of_columns_plate_3 = 0 
else: number_of_columns_plate_3 = (last_column_plate_3-first_column_plate_3 + 1)
if first_column_plate_4 == 0 : number_of_columns_plate_4 = 0 
else: number_of_columns_plate_4 = (last_column_plate_4-first_column_plate_4 + 1)
total_number_of_columns = number_of_columns_plate_1 + number_of_columns_plate_2 + number_of_columns_plate_3 + number_of_columns_plate_4

def run(ctx):
    
    # testing how many plates to extract
    if  first_column_plate_1 != 0 and \
        first_column_plate_2 == 0 and \
        first_column_plate_3 == 0 and \
        first_column_plate_4 == 0 : number_of_plates_to_extract = 1
    if  first_column_plate_1 != 0 and \
        first_column_plate_2 != 0 and \
        first_column_plate_3 == 0 and \
        first_column_plate_4 == 0 : number_of_plates_to_extract = 2
    if  first_column_plate_1 != 0 and \
        first_column_plate_2 != 0 and \
        first_column_plate_3 != 0 and \
        first_column_plate_4 == 0 : number_of_plates_to_extract = 3
    if  first_column_plate_1 != 0 and \
        first_column_plate_2 != 0 and \
        first_column_plate_3 != 0 and \
        first_column_plate_4 != 0 : number_of_plates_to_extract = 4


# Defining the functions executed in the protocols
    
    def pre_grinding_water_dispense():
        p300.pick_up_tip()
        for plate in plates:
            for d in plate:
                p300.aspirate(50, water_reservoir_01.bottom(z = 2.5), rate = 1)
                p300.air_gap(5)
                p300.dispense(50 + 5, d.top(2), rate = 2)
        p300.return_tip()

    def post_grinding_buffer_dispense():
        p300.pick_up_tip(tiprack_1.wells()[0])
        for plate in plates:
            for d in plate:
                p300.aspirate(buffer_volume, reservoir_01.bottom(z = 3), rate = 0.8)
                time.sleep(1)
                p300.air_gap(5)
                p300.dispense(buffer_volume + 5, d.top(2), rate = 2)
                #p300.blow_out(d.top(2)) # useless, it creates bubles on the tips end
        p300.return_tip()         
    
    def dispensing_chloroform_and_mixing(start_tiprack):                            # start_tiprack = tiprack_1
                                                                                                                                                              
        iteration1 = 0                                                              # Initializing a counter to keep track of the iterations
        iteration2 = 0                                                              # Initializing a counter to keep track of the iterations
        
        # Loop through the plates
        for plate in plates:

            # Increment the iteration counter
            iteration1 += 1
            
            # Loop through the wells in the plate
            for destination in plate:
                # Increment the iteration counter
                iteration2 += 1
                
                # Check if it's the first iteration of both loops
                if iteration1 == 1 and iteration2 == 1:
                    p300.pick_up_tip(start_tiprack["A1"])
                else:
                    p300.pick_up_tip()

                p300.aspirate(20, water_reservoir_01.bottom(z = 2.5), rate = 4) # Aspirating the water "Liquid-Cap"
                p300.aspirate(20, water_reservoir_01.top(z = 5), rate = 4)
                #p300.air_gap(150, rate = 4)
                p300.aspirate(255, reservoir_01.bottom(z = 2.5), rate = 4) # Chloroform pipetting
                p300.aspirate(5, location = reservoir_01.top(z = 2))
                p300.dispense(300, location = destination.top(z = 5), rate = 4)
                p300.aspirate(300, location = destination.top(z = 5), rate = 4)
                
                
                # This loop will mix the chloroform and extraction buffer by blowing air in the liquids
                i = 0                                   
                while i < 6: 
                    
                    p300.dispense(300, location = destination.bottom(z = 4), rate = 8)
                    p300.aspirate(300, location = destination.top(z = 5), rate = 4) 
                    i += 1

                p300.dispense(300, location = destination.bottom(z = 4), rate = 8)
                
                p300.touch_tip(destination, v_offset = -2, radius = 1.3, speed = 40)
                p300.touch_tip(destination, v_offset = -2, radius = 1.3, speed = 40)
                p300.drop_tip()


    time_dispensing_chloroform_and_mixing = 70                      # Defining a time (s) variable to calculate the duration of the step

    volume_1 = 140 #170                                             # First volume of supernatant to aspirate 
    volume_2 = 50 #90                                               # Second volume of supernatant to aspirate

    def isopropanol_dispensing():
        isopropanol_volume = (volume_1 + volume_2) * 0.7             # was set to 0.8 usualy
        #p300.pick_up_tip(transfer_tiprack_1["A1"])                  # transfer_tiprack_1 is always the firts tip rack for Isopropanol dispensing and supernanter stransfer
        p300.pick_up_tip(transfer_tiprack_1.rows()[0][first_column_plate_1 - 1])
        for plate in final_plates:
            for d in plate:
                p300.aspirate(isopropanol_volume, reservoir_01.bottom(z = 2.5))
                p300.air_gap(5)
                p300.dispense(isopropanol_volume + 5, d.top(2))
                #p300.blow_out(d.top(2))
                
        p300.return_tip()

    time_isopropanol_dispensing = 5                                 # Defining a time (s) variable to calculate the duration of the step
    
    def supernatant_transfer_and_mix(samples_plate, final_plate, transfer_tiprack):

        for s, d, t in zip(samples_plate, final_plate, transfer_tiprack):
            p300.pick_up_tip(location = t)
            p300.move_to(s.top(-16), speed = 400)
            p300.move_to(s.bottom(z = distance_interstice_to_bottom + 2.5), speed = 10)            # The z value is the distance to avoid touching the water-Chloroform interstice
            p300.aspirate(volume_1, s.bottom(z = distance_interstice_to_bottom + 3.5), rate = 0.2)      # The z value is the distance to avoid touching the water-Chloroform interstice
            p300.move_to(s.bottom(z = distance_interstice_to_bottom + 0.75), speed = 7)            # The z value is the distance to avoid touching the water-Chloroform interstice
            p300.aspirate(volume_2, s.bottom(z = distance_interstice_to_bottom + 1.5), rate = 0.1)      # The z value is the distance to avoid touching the water-Chloroform interstice
            p300.air_gap(5)
            p300.default_speed = 400
            p300.flow_rate.aspirate = 400                          # Set the aspirate flow rate to x µl/s
            p300.flow_rate.dispense = 2500                          # Set the dispense flow rate to x µl/s
            p300.dispense(volume_1 + volume_2, d.bottom(z = 9))

            # This loop will mix the liquids
            i = 0                                   
            while i < 5:
                p300.aspirate(250, location = d.bottom(z = 9), rate = 1)
                p300.dispense(250, location = d.bottom(z = 9), rate = 4)
                i += 1
            
            # Doing a blow out on the side walls
            center_location = d.center()
            p300.blow_out(center_location.move(types.Point(x = 1, y = 4, z = 16.5)))
            p300.blow_out(center_location.move(types.Point(x = 1, y = -4, z = 16.5)))
            #p300.drop_tip()                                       # Drop_tip with no arguments will drop the tips in the trash.     
            p300.drop_tip(location = t)                            # This will return the tip in the tip rack at the same location were it was attached. This can be usefull if we would like to reuse the tips for removing isopropanol and ethanol from wash.

    time_supernatant_transfer_and_mixing = 30   

    def isopropanol_discarding(final_plate, transfer_tiprack):
        for s, t in zip(final_plate, transfer_tiprack):
            p300.pick_up_tip(location = t)
            
            p300.move_to(location = s.bottom(8), speed = 400)         # Set this location to 1 mm above ethanol surface from the bottom of the 0.6 ml tube               
            p300.aspirate(location =  s.bottom(z = 8), volume = 245, rate = 0.2)
            
            p300.move_to(location = s.bottom(z = 4), speed = 10)            
            p300.aspirate(location = s.bottom(z = 4), volume = 30, rate = 0.1)
            
            p300.move_to(location = s.bottom(z = 3), speed = 10)            
            p300.aspirate(location = s.bottom(z = 3), volume = 10, rate = 0.05)
            
            p300.move_to(location = s.bottom(z = 2), speed = 10)            
            p300.aspirate(location = s.bottom(z = 2), volume = 5, rate = 0.02)
            
            p300.air_gap(5)
            
            p300.default_speed = 400
            p300.dispense(location = trash, volume = 300, rate = 3)              # Set the dispense flow rate to x µl/s
            p300.blow_out(location = trash)
            p300.drop_tip(location = t)                                         # Drop_tip with no arguments will drop the tips in the trash.
         
    def ethanol_dispensing():
        p300.pick_up_tip()
        for plate in final_plates:
            for f in plate:
                center_location = f.center()
                p300.aspirate(290, reservoir_01.bottom(z = 2.5))
                p300.air_gap(10)
                p300.dispense(300, center_location.move(types.Point(x = 1, y = 1, z = 18)), rate = 0.2) # Dispensing on the sidewall to avoid detachment of the DNA pellet at the bottom of the tubes.
                p300.blow_out(f.top())
        p300.drop_tip()

    def ethanol_discarding(final_plate, transfer_tiprack):
        for s, t in zip(final_plate, transfer_tiprack):
            p300.pick_up_tip(location = t)
            
            p300.move_to(location = s.bottom(7), speed = 400)         
            p300.aspirate(location = s.bottom(7), volume = 200, rate = 0.2)
            
            p300.move_to(location = s.bottom(z = 3), speed = 20)            
            p300.aspirate(location = s.bottom(z = 3), volume = 70, rate = 0.05)
            
            p300.move_to(location = s.bottom(z = 2), speed = 10)            
            p300.aspirate(location = s.bottom(z = 2), volume = 25, rate = 0.02)
            
            p300.air_gap(5)
            
            p300.default_speed = 400
            p300.drop_tip()                                         # Drop_tip with no arguments will drop the tips in the trash.     


    time_ethanol_discarding = 30                       # Defining a time (s) variable to calculate the duration of the step

    def EBbuffer_dispensing():
            p300.pick_up_tip()    
            for plate in final_plates:   
                for f in plate:
                    p300.aspirate(elution_buffer_volume, reservoir_01.bottom(z = 2.5))
                    p300.air_gap(10)
                    p300.dispense(elution_buffer_volume + 10, f.top(0))
                    p300.blow_out(f.top(1))
            p300.drop_tip()

    def truncate(n, decimals=0):                # This function is used to round decimal number for time calculation
        multiplier = 10**decimals
        return int(n * multiplier) / multiplier


    def blinking_light():
        # Get the OT-2's rail light module
        rail_lights = ctx._driver._backend._modules['lights']

        # Define the duration of each state (on/off) of the rail light in seconds
        blink_duration = 1.0

        # Define the total number of blinks
        num_blinks = 10

        # Blink the rail light for the specified number of times
        for i in range(num_blinks):
            # Turn the rail light on
            rail_lights.set_rail_lights(on=True)

            # Wait for the specified duration
            time.sleep(blink_duration)

            # Turn the rail light off
            rail_lights.set_rail_lights(on=False)

            # Wait for the specified duration
            time.sleep(blink_duration)

        
################################            ##    
#                              #          ####
# ONE plate (96-well) protocol #            ##
#                              #            ##    
################################           ####    
    if number_of_plates_to_extract == 1 :

        # Load Labware
        tiprack_1 = ctx.load_labware(tipsbox, '2')
        transfer_tiprack_1 = ctx.load_labware(tipsbox, '7')
        tiprack_9 = ctx.load_labware(tipsbox, '5')
        samples_plate_1 = ctx.load_labware(samples_plate_type, '1')
        final_plate_1 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', '4')
        reservoir_1 = ctx.load_labware(reservoir_type, '3')
        water_reservoir = ctx.load_labware(reservoir_type, '6')
        trash = ctx.fixed_trash['A1'].top(z=-10)

        # Load Instrument
        p300 = ctx.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1, transfer_tiprack_1, tiprack_9])
    
        # Subset only the columns with samples in your plates
        samples_P1 = samples_plate_1.rows()[0][first_column_plate_1 - 1:last_column_plate_1]
        plates = [samples_P1]

        #buffer_chloroform_tiprack_1 = tiprack_1.rows()[0][first_column_plate_1 - 1:last_column_plate_1]
        #buffer_chloroform_tipracks = [buffer_chloroform_tiprack_1]

        final_plate_01 = final_plate_1.rows()[0][first_column_plate_1 - 1:last_column_plate_1]
        final_plates = [final_plate_01]

        transfer_tiprack_01 = transfer_tiprack_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
        transfer_tipracks = [transfer_tiprack_01]

        reservoir_01 = reservoir_1.wells()[0]
        water_reservoir_01 = water_reservoir.wells()[0]



        ########################
        # DNA extraction actions
        ########################
        ctx.pause('''Turn on and set incubator bath at 65C''')
        ctx.pause('''Setup: Samples_plates (site 1), tipracks (site 2, 5 & 7)''')
        ctx.pause('''Place DD-water reservoir on site 6''')
        ctx.pause('''Start "pre-grinding" water dispensing  to samples on site 1''')

        pre_grinding_water_dispense()

        ctx.pause('''Grind samples on a tyssus-lyser machine''')
        ctx.pause('''Place plate back to site 1 and continue adding extraction buffer to samples''')
        ctx.pause('''Place buffer reservoir on site 3''')
        ctx.pause('''Start post-grinding Extraction buffer dispensing to samples on site 1''')

        post_grinding_buffer_dispense()

        ctx.pause('''Incubate the plate (65C, 30 min)''')
        ctx.pause('''After the 30 minute incubation, place the plate back on site 1 ''')
        ctx.pause('''Remove Extraction buffer reservoir on site 3 and place Chloroform reservoir on site 3''')
        ctx.pause('''Start Chloroform dispensing and mixing to samples plate on site 1''')

        #comment = string1 + string2 + str(truncate((time_dispensing_chloroform * total_number_of_columns / 60) + (time_dispensing_chloroform_and_mixing * total_number_of_columns / 60), 1)) + string3 + string1
        #ctx.pause(comment)

        dispensing_chloroform_and_mixing(start_tiprack = tiprack_1)

        ctx.pause('''Centrifugate the plate (6000rpm, 10 min). During centrifugation add Isopropanol to empty T110-2 plate on site 4''') 
        ctx.pause('''Remove Chloroform reservoir on site 3 and place Isopropanol reservoir on site 3''')
        ctx.pause('''Identify with Sharpie pen and place an empty T110-2 plate (with 0.6ml incert tubes) on site 4''')
        ctx.pause('''Start Isopropanol dispensing to plate on site 4''')

        p300.starting_tip = transfer_tiprack_1.wells()[first_column_plate_1 - 1]

        isopropanol_dispensing()

        ctx.pause('''When the 10 minutes centrifugation is done place the sample plate back on sites 1 and the T110-2 plate with Isopropanol dispenced should be on site 4''')
        ctx.pause('''Start supernatant transfer from samples plate to final plate''')
        comment = string1 + string2 + str(truncate(time_supernatant_transfer_and_mixing * total_number_of_columns / 60, 1)) + string3 + string1 # Time estimation
        ctx.pause(comment)
        
        for samples, final, tiprack in zip(plates, final_plates, transfer_tipracks):
                    supernatant_transfer_and_mix(samples, final, tiprack)

        ctx.pause('''Centrifugate the plate for 30 minutes à 6000 rpm and prepare cold 70 percent ethanol''')
        ctx.pause('''When the 30 minutes centrifugation is done, prepare for supernatant discarding with the robot''')
        ctx.pause('''Place the final samples plate back to sites 4''')
        ctx.pause('''Start discarding supernatant''')
        
        for final, tiprack in zip(final_plates, transfer_tipracks):
            isopropanol_discarding(final, tiprack)

        ctx.pause('''Remove Isopropanol reservoir on site 3, add Ethanol 70 percent reservoir to site 3''')
        ctx.pause('''Start Ethanol dispensing to plate on site 4''')

        p300.starting_tip = tiprack_9.wells()[0] #Going back to previously started tip rack

        ethanol_dispensing()

        ctx.pause('''Centrifugate the plate for 30 minutes à 6000 rpm''')
        ctx.pause('''When the 30 minute centrifugation is done, place the plate back on site 3 to discard ethanol with the robot''')
        ctx.pause('''Start discarding the ethanol on site 4''')

        for final, tiprack in zip(final_plates, transfer_tipracks):
            ethanol_discarding(final, tiprack)

        ctx.pause('''Evaporate residual ethanol for X minutes at 45 degrees celsius''')
        ctx.pause('''Prepare for EB buffer dispensing: remove Ethanol reservoir on site 3, EB buffer on site 3''')
        ctx.pause('''When evaporation is done, place plate back to site 4''')
        ctx.pause('''Start EB buffer dispensing''')

        EBbuffer_dispensing()

        ctx.comment('\n~~~~~~~~~~~~~~Protocol Complete~~~~~~~~~~~~~~\n')

    else:

###############################          ####
#                             #        ##    ##
# TWO plates 96-well protocol #             ##
#                             #           ##        
###############################         #######
        if number_of_plates_to_extract == 2 :

            # Load Labware
            tiprack_1 = ctx.load_labware(tipsbox, '6')
            tiprack_2 = ctx.load_labware(tipsbox, '9')
            transfer_tiprack_1 = ctx.load_labware(tipsbox, '7')
            transfer_tiprack_2 = ctx.load_labware(tipsbox, '8')
            tiprack_9 = ctx.load_labware(tipsbox, '10')
            samples_plate_1 = ctx.load_labware(samples_plate_type, '1')
            samples_plate_2 = ctx.load_labware(samples_plate_type, '2')
            final_plate_1 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', '4')
            final_plate_2 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', '5')
            reservoir_1 = ctx.load_labware(reservoir_type, '3')
            water_reservoir = ctx.load_labware(reservoir_type, '11')
            trash = ctx.fixed_trash['A1'].top(z=-10)

            # Load Instrument
            p300 = ctx.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1, tiprack_2, transfer_tiprack_1, transfer_tiprack_2, tiprack_9])
    
            # Subset only the columns with samples in your plates
            samples_P1 = samples_plate_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
            samples_P2 = samples_plate_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
            plates = [samples_P1, samples_P2]
            
            #buffer_chloroform_tiprack_1 = tiprack_1.rows()[0][first_column_plate_1 - 1:last_column_plate_1]
            #buffer_chloroform_tiprack_2 = tiprack_2.rows()[0][first_column_plate_2 - 1:last_column_plate_2]
            #buffer_chloroform_tipracks = [buffer_chloroform_tiprack_1, buffer_chloroform_tiprack_2]
            
            final_plate_01 = final_plate_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
            final_plate_02 = final_plate_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
            final_plates = [final_plate_01, final_plate_02]

            transfer_tiprack_01 = transfer_tiprack_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
            transfer_tiprack_02 = transfer_tiprack_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
            transfer_tipracks = [transfer_tiprack_01, transfer_tiprack_02]
            
            reservoir_01 = reservoir_1.wells()[0]
            water_reservoir_01 = water_reservoir.wells()[0]

            ########################
            # DNA extraction actions
            ########################
            ctx.pause('''Turn on and set incubator bath at 65C''')
            ctx.pause('''Place Samples plates on sites 1 & 2 and write down the site on the plate (Ex: Plate-AA = Site-1, Plate-BB = Site-2 ...)''')
            ctx.pause('''Place tip racks on site 6, 7, 8, 9 and 10''')
            ctx.pause('''Place DD-water reservoir on site 11''')
            ctx.pause('''Start "pre-grinding" water dispensing to samples''')
            
            pre_grinding_water_dispense()
            
            ctx.pause('''Grind samples on a tyssus-lyser machine''')
            ctx.pause('''Place plate back to site 1 & 2 and continue adding extraction buffer to samples''')
            ctx.pause('''Place Extraction buffer reservoir on site 3''')
            ctx.pause('''Start dispensing of Extraction buffer to samples''')

            post_grinding_buffer_dispense()

            ctx.pause('''Place the plates at 65 celsius in water bath for 30 minutes''')
            ctx.pause('''When the 30 minutes incubation is done, place the samples plates back on site 1 & 2''')
            ctx.pause('''Remove Extraction buffer reservoir on site 3, place Chloroform reservoir on site 3''')
            ctx.pause('''Start Chloroform dispensing to plates on site 1 & 2''')
            
            #comment = string1 + string2 + str(truncate((time_dispensing_chloroform * total_number_of_columns / 60) + (time_dispensing_chloroform_and_mixing * total_number_of_columns / 60), 1)) + string3 + string1
            #ctx.pause(comment)

            dispensing_chloroform_and_mixing(start_tiprack = tiprack_1)

            ctx.pause('''During centrifugation add Isopropanol to empty T110-2 plate on site 4 & 5''')
            ctx.pause('''Centrifuge the plates for 10 minutes at 6000 rpm and During centrifugation the robot will add Isopropanol to empty T110-2 plates on site 4 & 5''')
            ctx.pause('''Remove Chloroform reservoir on site 3 and place Isopropanol reservoir on site 3''')
            ctx.pause('''Identify with Sharpie pen and place empty T110-2 plates on site 4 & 5''')
            ctx.pause('''Start Isopropanol dispensing to plates on site 4 & 5 and centrifuge the samples plates for 10 minutes at 6000 rpm''')

            # starting the transfer with a new tiprack (this would be usefull if we would like to reuse the tips)
            p300.starting_tip = transfer_tiprack_1.wells()[first_column_plate_1 - 1] 

            isopropanol_dispensing()

            ctx.pause('''When the 10 minutes centrifugation is done place the sample plates back on sites 1 & 2 and the T110-2 plate with Isopropanol dispenced should be on site 4 and 5''')
            ctx.pause('''Start supernatant transfer from samples plates to final plates''')
            comment = string1 + string2 + str(truncate(time_supernatant_transfer_and_mixing * total_number_of_columns / 60, 1)) + string3 + string1 # Time estimation
            ctx.pause(comment)
               
            for samples, final, tiprack in zip(plates, final_plates, transfer_tipracks):
                    supernatant_transfer_and_mix(samples, final, tiprack)

            ctx.pause('''Centrifugate the plates for 10 minutes at 6000 rpm and prepare cold 70 percent ethanol''')
            ctx.pause('''When the 10 minutes centrifugation is done, prepare for supernatant discarding with the robot''')
            ctx.pause('''Place the final samples plate back to sites 4 & 5''')
            ctx.pause('''Start discarding supernatant''')

            for final, tiprack in zip(final_plates, transfer_tipracks):
                isopropanol_discarding(final, tiprack)
            
            ctx.pause('''Remove Isopropanol reservoir on site 3, add Ethanol 70 percent reservoir to site 3''')
            ctx.pause('''Start Ethanol dispensing to plates on site 4 & 5''')

            p300.starting_tip = tiprack_9.wells()[1] #Going back to previously started tip rack

            ethanol_dispensing()

            ctx.pause('''Centrifugate the plates for 10 minutes at 6000 rpm''')
            ctx.pause('''When the 10 minute centrifugation is done, place the plate back on site 4 & 5 to discard ethanol with the robot''')
            ctx.pause('''Start discarding the ethanol on site 4 & 5''')

            for final, tiprack in zip(final_plates, transfer_tipracks):
                ethanol_discarding(final, tiprack)

            ctx.pause('''Evaporate residual ethanol for X minutes at 45 degrees celsius''')
            ctx.pause('''Prepare for EB buffer dispensing: remove Ethanol reservoir on site 3, EB buffer on site 3''')
            ctx.pause('''When evaporation is done, place plates back to site 4 & 5''')
            ctx.pause('''Start EB buffer dispensing''')

            EBbuffer_dispensing()

            ctx.comment('\n~~~~~~~~~~~~~~Protocol Complete~~~~~~~~~~~~~~\n')
        
        else:
             
#################################            ###
#                               #           #  ##
# THREE plates 96-well protocol #             ##
#                               #           #  ##
#################################            ###
             
            if number_of_plates_to_extract == 3 :

                # Load Labware
                tiprack_1 = ctx.load_labware(tipsbox, '7')
                tiprack_2 = ctx.load_labware(tipsbox, '8')
                tiprack_3 = ctx.load_labware(tipsbox, '9')
                transfer_tiprack_1 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                transfer_tiprack_2 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                transfer_tiprack_3 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                tiprack_9 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                samples_plate_1 = ctx.load_labware(samples_plate_type, '1')
                samples_plate_2 = ctx.load_labware(samples_plate_type, '2')
                samples_plate_3 = ctx.load_labware(samples_plate_type, '3')
                final_plate_1 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', '4')
                final_plate_2 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', '5')
                final_plate_3 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', '6')
                reservoir_1 = ctx.load_labware(reservoir_type, '10')
                water_reservoir = ctx.load_labware(reservoir_type, '11')
                trash = ctx.fixed_trash['A1'].top(z=-10)

                # Load Instrument
                p300 = ctx.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1, tiprack_2, tiprack_3, transfer_tiprack_1, transfer_tiprack_2, transfer_tiprack_3, tiprack_9])
        
                # Subset only the columns with samples in your plates
                samples_P1 = samples_plate_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
                samples_P2 = samples_plate_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
                samples_P3 = samples_plate_3.rows()[0][first_column_plate_3 - 1 : last_column_plate_3]
                plates = [samples_P1, samples_P2, samples_P3]                
                
                final_plate_01 = final_plate_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
                final_plate_02 = final_plate_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
                final_plate_03 = final_plate_3.rows()[0][first_column_plate_3 - 1 : last_column_plate_3]
                final_plates = [final_plate_01, final_plate_02, final_plate_03]
                
                transfer_tiprack_01 = transfer_tiprack_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
                transfer_tiprack_02 = transfer_tiprack_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
                transfer_tiprack_03 = transfer_tiprack_3.rows()[0][first_column_plate_3 - 1 : last_column_plate_3]
                transfer_tipracks = [transfer_tiprack_01, transfer_tiprack_02, transfer_tiprack_03]               
                
                reservoir_01 = reservoir_1.wells()[0]
                water_reservoir_01 = water_reservoir.wells()[0]

                ctx.pause('''Turn on and set incubator bath at 65C''')
                ctx.pause('''Place Samples plates on sites 1, 2, 3, 7 and write down the site on the plate (Ex: Plate-AA = Site-1, Plate-BB = Site-2 ...)''')
                ctx.pause('''Place tip racks on site 5, 6, 8 and 9''')
                ctx.pause('''Place DD-water reservoir on site 11''')
                ctx.pause('''Start pre-grinding water dispensing to samples''')
                
                pre_grinding_water_dispense()
                
                ctx.pause('''Grind samples on a tyssus-lyser machine''')
                ctx.pause('''After grinding, place the plate back on site 1, 2 and 3 ''')
                ctx.pause('''Place Extraction buffer reservoir on site 10''')
                ctx.pause('''Start post-grinding Extraction buffer dispensing to samples on site 1, 2 and 3''')
                
                #p300.starting_tip = tiprack_1.wells()[0]
                post_grinding_buffer_dispense()
                
                ctx.pause('''Incubate the plates (65C, 30 min)''')
                ctx.pause('''After the 30 minute incubation, place the plate back on site 1, 2 and 3 ''')
                ctx.pause('''Remove Extraction buffer reservoir on site 11, place Chloroform reservoir on site 1''')
                ctx.pause('''Start Chloroform dispensing and mixing to plates''')
                
                #comment = string1 + string2 + str(truncate((time_dispensing_chloroform * total_number_of_columns / 60) + (time_dispensing_chloroform_and_mixing * total_number_of_columns / 60), 1)) + string3 + string1
                #ctx.pause(comment)
                
                dispensing_chloroform_and_mixing(start_tiprack = tiprack_1)

                ctx.pause('''Centrifuge the plates for 10 minutes at 6000 rpm. During centrifugation the robot will add Isopropanol to empty T110-2 plates on site 4, 5 and 6''')
                ctx.pause('''During centrifugation the robot will add Isopropanol to empty T110-2 plates on site 4, 5 and 6''') 
                ctx.pause('''Remove Chloroform reservoir on site 10 and place Isopropanol reservoir on site 10''')
                ctx.pause('''Remove empty tip racks on sites 7, 8 and 9 and place new tip racks on sites 7, 8 and 9''')
                ctx.pause('''Identify with Sharpie pen and place empty T110-2 plates on site 4, 5 and 6''')
                ctx.pause('''Start Isopropanol dispensing to plates on site 4, 5 and 6''')

                for tiprack in [tiprack_1, tiprack_2, tiprack_3]:
                    ctx.move_labware(labware = tiprack, new_location = protocol_api.OFF_DECK)

                ctx.move_labware(labware = transfer_tiprack_1, new_location = 7)
                ctx.move_labware(labware = transfer_tiprack_2, new_location = 8)
                ctx.move_labware(labware = transfer_tiprack_3, new_location = 9)

                # starting the transfer with a new tip rack (this would be usefull if we would like to reuse the tips)
                p300.starting_tip = transfer_tiprack_1.wells()[first_column_plate_1 - 1] 

                isopropanol_dispensing()

                ctx.pause('''When the 10 minutes centrifugation is done place the "starting sample plates" back on sites 1, 2 and 3 and the T110-2 plate with Isopropanol added should be on site 4, 5 and 6''')               
                
                #comment = string1 + string2 + str(truncate(time_supernatant_transfer_and_mixing * total_number_of_columns / 60), 1) + string3 + string1
                #ctx.pause(comment)
                
                ctx.pause('''Start supernatant transfer from starting plates to final plates''')

                for samples, final, tiprack in zip(plates, final_plates, transfer_tipracks):
                    supernatant_transfer_and_mix(samples, final, tiprack)

                ctx.pause('''Centrifugate the plates for 10 minutes at 6000 rpm and prepare cold 70 percent ethanol''')
                ctx.pause('''When the 10 minutes centrifugation is done, prepare for supernatant discarding with the robot''')
                ctx.pause('''Place the final samples plate back to sites 4, 5, 6''')
                ctx.pause('''Start discarding supernatant''')

                for final, tiprack in zip(final_plates, transfer_tipracks):
                    isopropanol_discarding(final, tiprack)

                ctx.pause('''Remove Isopropanol reservoir on site 10, add Ethanol 70 percent reservoir to site 10''')
                ctx.move_labware(labware = water_reservoir, new_location = protocol_api.OFF_DECK)
                ctx.move_labware(labware = tiprack_9, new_location = 11)
                ctx.pause('''Start Ethanol dispensing to plates on site 4, 5, 6''')

                p300.starting_tip = tiprack_9.wells_by_name()['A1']

                ethanol_dispensing()

                ctx.pause('''Centrifugate the plates for 10 minutes at 6000 rpm''')
                ctx.pause('''When the 10 minute centrifugation is done, place the plate back on site 4 & 5 to discard ethanol with the robot''')
                ctx.pause('''Start discarding the ethanol on site 4 & 5''')

                for final, tiprack in zip(final_plates, transfer_tipracks):
                    ethanol_discarding(final, tiprack)

                ctx.pause('''Evaporate residual ethanol for X minutes at 45 degrees celsius''')
                ctx.pause('''Prepare for EB buffer dispensing: remove Ethanol reservoir on site 3, EB buffer on site 3''')
                ctx.pause('''When evaporation is done, place plates back to site 4 & 5''')
                ctx.pause('''Start EB buffer dispensing''')

                EBbuffer_dispensing()
            
            else:
                
#################################             ##    ##
#                               #             ##    ##
# FOUR plates 96-well protocol  #             ########      
#                               #                   ##
#################################                   ##
                 
                 if number_of_plates_to_extract == 4 :

                    # Load Labware
                    tiprack_1 = ctx.load_labware(tipsbox, '8')
                    tiprack_2 = ctx.load_labware(tipsbox, '9')
                    tiprack_3 = ctx.load_labware(tipsbox, '5')
                    tiprack_4 = ctx.load_labware(tipsbox, '6')
                    transfer_tiprack_1 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                    transfer_tiprack_2 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                    transfer_tiprack_3 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                    transfer_tiprack_4 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                    tiprack_9 = ctx.load_labware(tipsbox, protocol_api.OFF_DECK)
                    samples_plate_1 = ctx.load_labware(samples_plate_type, '1')
                    samples_plate_2 = ctx.load_labware(samples_plate_type, '2')
                    samples_plate_3 = ctx.load_labware(samples_plate_type, '3')
                    samples_plate_4 = ctx.load_labware(samples_plate_type, '7')
                    final_plate_1 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', protocol_api.OFF_DECK)
                    final_plate_2 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', protocol_api.OFF_DECK)
                    final_plate_3 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', protocol_api.OFF_DECK)
                    final_plate_4 = ctx.load_labware('0.6mlsimportvwrt1102_96_wellplate_600ul', protocol_api.OFF_DECK)
                    reservoir_1 = ctx.load_labware(reservoir_type, '11')
                    water_reservoir = ctx.load_labware(reservoir_type, '10')
                    trash = ctx.fixed_trash['A1'].top(z=-10)

                    # Load Instrument
                    p300 = ctx.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1, tiprack_2, tiprack_3, tiprack_4, transfer_tiprack_1, transfer_tiprack_2, transfer_tiprack_3, transfer_tiprack_4, tiprack_9])
            
                    # Subset only the columns with samples in your plates
                    samples_P1 = samples_plate_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
                    samples_P2 = samples_plate_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
                    samples_P3 = samples_plate_3.rows()[0][first_column_plate_3 - 1 : last_column_plate_3]
                    samples_P4 = samples_plate_4.rows()[0][first_column_plate_4 - 1 : last_column_plate_4]
                    plates = [samples_P1, samples_P2, samples_P3, samples_P4]                
                    
                    final_plate_01 = final_plate_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
                    final_plate_02 = final_plate_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
                    final_plate_03 = final_plate_3.rows()[0][first_column_plate_3 - 1 : last_column_plate_3]
                    final_plate_04 = final_plate_4.rows()[0][first_column_plate_4 - 1 : last_column_plate_4]
                    final_plates = [final_plate_01, final_plate_02, final_plate_03, final_plate_04]
                    
                    transfer_tiprack_01 = transfer_tiprack_1.rows()[0][first_column_plate_1 - 1 : last_column_plate_1]
                    transfer_tiprack_02 = transfer_tiprack_2.rows()[0][first_column_plate_2 - 1 : last_column_plate_2]
                    transfer_tiprack_03 = transfer_tiprack_3.rows()[0][first_column_plate_3 - 1 : last_column_plate_3]
                    transfer_tiprack_04 = transfer_tiprack_4.rows()[0][first_column_plate_4 - 1 : last_column_plate_4]
                    transfer_tipracks = [transfer_tiprack_01, transfer_tiprack_02, transfer_tiprack_03, transfer_tiprack_04]               
                    
                    reservoir_01 = reservoir_1.wells()[0]
                    water_reservoir_01 = water_reservoir.wells()[0]

                    ctx.pause('''Turn on and set incubator bath at 65C''')
                    ctx.pause('''Place Samples plates on sites 1, 2, 3 and write down the site on the plate (Ex: Plate-AA = Site-1, Plate-BB = Site-2 ...)''')
                    ctx.pause('''Place tip racks on site 7, 8 and 9''')
                    ctx.pause('''Place DD-water reservoir on site 10''')
                    ctx.pause('''Start pre-grinding water dispensing''')

                    pre_grinding_water_dispense()

                    ctx.pause('''Grind samples on a tyssus-lyser machine''')
                    ctx.pause('''After grinding, place the plate back on site 1, 2, 3 ''')
                    ctx.pause('''Place Extraction buffer reservoir on site 11''')
                    ctx.pause('''Start post-grinding Extraction buffer dispensing''')

                    post_grinding_buffer_dispense()

                    ctx.pause('''Incubate the plates (65C, 30 min)''')
                    ctx.pause('''After the 30 minute incubation, place the plate back on site 1, 2, 3 ''')
                    ctx.pause('''Remove Extraction buffer reservoir on site 10, place Chloroform reservoir on sit 10 and place Water reservoir on site 11''')
                    ctx.pause('''Start Chloroform dispensing and mixing to plates''')
                    
                    #comment = string1 + string2 + str(truncate((time_dispensing_chloroform * total_number_of_columns / 60) + (time_dispensing_chloroform_and_mixing * total_number_of_columns / 60), 1)) + string3 + string1
                    #ctx.pause(comment)
       
                    dispensing_chloroform_and_mixing(start_tiprack = tiprack_1)

                    ctx.pause('''Centrifuge the plates for 10 minutes at 6000 rpm and During centrifugation the robot will add Isopropanol to empty T110-2 plates on site 4, 5, 6 and 10''')
                    ctx.pause('''Remove empty tip racks on sites 5, 6, 8 and 9 and place new tip racks on sites 8 and 9''')
                    
                    for tiprack in [tiprack_1, tiprack_2, tiprack_3, tiprack_4]:
                        ctx.move_labware(labware = tiprack, new_location = protocol_api.OFF_DECK)

                    ctx.move_labware(labware = water_reservoir, new_location = protocol_api.OFF_DECK)

                    ctx.move_labware(labware = transfer_tiprack_1, new_location = 8)
                    ctx.move_labware(labware = transfer_tiprack_2, new_location = 9)

                    ctx.pause('''Place empty T110-2 plates with 0.6ml insert tubes on site 4, 5, 6 and 10 (identify the plates and mark site number)''')

                    ctx.move_labware(labware = final_plate_1, new_location = 4)
                    ctx.move_labware(labware = final_plate_2, new_location = 5)
                    ctx.move_labware(labware = final_plate_3, new_location = 6)
                    ctx.move_labware(labware = final_plate_4, new_location = 10)

                    ctx.pause('''Remove Chloroform reservoir on site 11 and place Isopropanol reservoir on site 11''')
                    ctx.pause('''Start Isopropanol dispensing to empty plates''')

                    # starting the transfer with a new tip rack
                    p300.starting_tip = transfer_tiprack_1.wells()[first_column_plate_1 - 1] 

                    isopropanol_dispensing()

                    ctx.pause('''When the 10 minutes centrifugation is done place the Sample plates back on sites 1, 2, 3 and 7 and the T110-2 plate with Isopropanol dispenced should be on site 4, 5, 6 and 10''')

                    # Redefining vectors since we have only two tipracks on the deck
                    plates = [samples_P1, samples_P2]
                    final_plates =[final_plate_01, final_plate_02]
                    transfer_tipracks = [transfer_tiprack_01, transfer_tiprack_02]

                    #the next comments are buggy
                    #comment = string1 + string2 + str(truncate((time_supernatant_transfer_and_mixing * total_number_of_columns / 60) / 2), 1) + string3 + string1
                    #ctx.pause(comment)
                    ctx.pause('''Start supernatant transfer and mixing''')

                    for samples, final, tiprack in zip(plates, final_plates, transfer_tipracks):
                        supernatant_transfer_and_mix(samples, final, tiprack)

                    ctx.pause('''Centrifugate the plates for 10 minutes at 6000 rpm''')
                    ctx.pause('''Remove Samples plates on sites 1 and 2 and place tip racks on sites 1 and 2''')
                
                    for plate in [samples_plate_1, samples_plate_2]:
                        ctx.move_labware(labware = plate, new_location = protocol_api.OFF_DECK)
                
                    ctx.move_labware(labware = transfer_tiprack_3, new_location = 2)
                    ctx.move_labware(labware = transfer_tiprack_4, new_location = 1)

                    p300.starting_tip = transfer_tiprack_3.wells()[first_column_plate_3 - 1]
                    
                    #comment = string1 + string2 + str(truncate((time_supernatant_transfer_and_mixing * total_number_of_columns / 60) / 2), 1) + string3 + string1
                    #ctx.pause(comment)
                    #ctx.pause('''Start supernatant transfer and mixing''')

                    # Redefining vectors since we have only two tipracks on the deck
                    plates = [samples_P3, samples_P4]
                    final_plates =[final_plate_03, final_plate_04]
                    transfer_tipracks = [transfer_tiprack_03, transfer_tiprack_04]

                    for samples, final, tiprack in zip(plates, final_plates, transfer_tipracks):
                        supernatant_transfer_and_mix(samples, final, tiprack)

                    ctx.pause('''Centrifugate the plates for 10 minutes at 6000 rpm''')
                    ctx.pause('''After centrifugation, place back the final samples plates to respective sites 4, 5, 6 and 10''')
                    ctx.pause('''Remove plates on sites 3 and 7''')
                    
                    for plate in [samples_plate_3, samples_plate_4]:
                        ctx.move_labware(labware = plate, new_location = protocol_api.OFF_DECK)

                    # Redefining vectors
                    final_plates =[final_plate_01, final_plate_02, final_plate_03, final_plate_04]
                    transfer_tipracks = [transfer_tiprack_01, transfer_tiprack_02, transfer_tiprack_03, transfer_tiprack_04]
                    
                    ctx.pause('''Start discarding isopropanol with the robot''')
                    for final, tiprack in zip(final_plates, transfer_tipracks):
                        isopropanol_discarding(final, tiprack)
                    
                    ctx.pause('''Prepare 70'%' Ethanol dispensing''')
                    ctx.pause('''Remove Isopropanol reservoir on site 11 and place 70'%'Ethanol reservoir to site 11''')
                    ctx.pause('''Place a tiprack on site 3''')
                    ctx.move_labware(labware = tiprack_9, new_location = 3)

                    #p300.starting_tip = tiprack_9.wells_by_name()['A1']
                    p300.starting_tip = tiprack_9.wells()[0]

                    ctx.pause('''Start Ethanol dispensing to plates on site 4, 5, 6 and 10''')

                    ethanol_dispensing()

                    ctx.pause('''Centrifugate the plates for 10 minutes at 6000 rpm''')
                    ctx.pause('''After centrifugation, place back the final samples plates to respective sites 4, 5, 6 and 10''')
                    ctx.pause('''Start discarding surpernatant with the robot''')

                    for final, tiprack in zip(final_plates, transfer_tipracks):
                        ethanol_discarding(final, tiprack)

                    ctx.pause('''Evaporate residual ethanol for X minutes at 45 degrees celsius''')
                    ctx.pause('''Prepare for EB buffer dispensing: remove Ethanol reservoir on site 11, EB buffer on site 11''')
                    ctx.pause('''When evaporation is done, place plates back to site 4, 5, 6 and 10''')
                    ctx.pause('''Start EB buffer dispensing''')

                    ctx.comment('\n~~~~~~~~~~~~~~ Dispensing EB buffer to samples ~~~~~~~~~~~~~~')

                    EBbuffer_dispensing()

                    ctx.comment('\n~~~~~~~~~~~~~~Protocol Complete~~~~~~~~~~~~~~\n')
