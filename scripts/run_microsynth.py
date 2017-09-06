#!/usr/bin/env python3

# run script for Household microsynthesis

import sys
import time
import humanleague
import ukcensusapi.Nomisweb as Api
import household_microsynth.microsynthesis as Microsynthesiser
import household_microsynth.utils as Utils

assert humanleague.version() == 1
CACHE_DIR = "./cache"

# # Set country or local authority/ies here
# REGION = "City of London"
# #REGION = "Newcastle upon Tyne"
# # Set resolution LA/MSOA/LSOA/OA
# RESOLUTION = Api.Nomisweb.OA

# The microsynthesis makes use of the following tables:
# LC4402EW - Accommodation type by type of central heating in household by tenure
# LC4404EW - Tenure by household size by number of rooms
# LC4405EW - Tenure by household size by number of bedrooms
# LC4408EW - Tenure by number of persons per bedroom in household by household type
# LC1105EW - Residence type by sex by age
# KS401EW - Dwellings, household spaces and accommodation type
# QS420EW - Communal establishment management and type - Communal establishments
# QS421EW - Communal establishment management and type - People
# TODO
# LC4202EW - Tenure by car or van availability by ethnic group of Household Reference Person (HRP)
# LC4601EW - Tenure by economic activity by age - Household Reference Persons
# TODO: differentiate between purpose-built and converted flats?

def main(region, resolution):

  # start timing
  start_time = time.time()

  print("Microsynthesis region: ", region)
  print("Microsynthesis resolution: ", resolution)
  msynth = Microsynthesiser.Microsynthesis(region, resolution, CACHE_DIR)
  # init microsynthesis
  # try:
  #   msynth = Microsynthesiser.Microsynthesis(region, resolution, CACHE_DIR)
  # except ValueError as e:
  #   print(e)
  #   return
  # except:
  #   print("Unknown exception")
  #   return

  # Do some basic checks on totals
  total_occ_dwellings = sum(msynth.lc4402.OBS_VALUE)
  assert sum(msynth.lc4404.OBS_VALUE) == total_occ_dwellings
  assert sum(msynth.lc4405.OBS_VALUE) == total_occ_dwellings
  assert sum(msynth.lc4408.OBS_VALUE) == total_occ_dwellings
  assert sum(msynth.ks401[msynth.ks401.CELL == 5].OBS_VALUE) == total_occ_dwellings

  total_population = sum(msynth.lc1105.OBS_VALUE)
  total_households = sum(msynth.ks401.OBS_VALUE)
  total_communal = sum(msynth.communal.OBS_VALUE)
  total_dwellings = total_households + total_communal

  occ_pop_lbound = sum(msynth.lc4404.C_SIZHUK11 * msynth.lc4404.OBS_VALUE)
  household_dwellings = sum(msynth.lc1105[msynth.lc1105.C_RESIDENCE_TYPE == 1].OBS_VALUE)
  communal_dwellings = sum(msynth.lc1105[msynth.lc1105.C_RESIDENCE_TYPE == 2].OBS_VALUE)

  print("Households: ", total_households)
  print("Occupied households: ", total_occ_dwellings)
  print("Unoccupied dwellings: ", total_households - total_occ_dwellings)
  print("Communal residences: ", total_communal)
  print("Dwellings: ", total_dwellings)

  print("Total dwellings: ", total_dwellings)
  print("Population in occupied households: ", household_dwellings)
  print("Population in communal residences: ", communal_dwellings)
  print("Population lower bound from occupied households: ", occ_pop_lbound)
  print("Occupied household dwellings underestimate: ", household_dwellings - occ_pop_lbound)

  print("Number of geographical areas: ", len(msynth.lc4402.GEOGRAPHY_CODE.unique()))

  # generate the population
  try:
    msynth.run()
  except ValueError as e:
    print(e)
    return
  except:
    print("Unknown exception")
    return

  print("Done. Exec time(s): ", time.time() - start_time)

  print("Checking consistency")
  Utils.check(msynth, total_occ_dwellings, total_households, total_communal)

  output = "./synHouseholds.csv"
  print("Writing synthetic population to", output)
  msynth.dwellings.to_csv(output)

  print("DONE")

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<region(s)> <resolution>")
    print("e.g:", sys.argv[0], "\"Newcastle upon Tyne\" OA")
    print("    ", sys.argv[0], "\"Leeds, Bradford\" MSOA")
  else:  
    region = sys.argv[1]
    resolution = sys.argv[2]
    main(region, resolution) 
