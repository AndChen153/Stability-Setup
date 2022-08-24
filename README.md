# Stability-Setup
Stability Tester for Perovskite Devices Summer 2022 JP lab

Capable of performing backwards and forwards JV scan at differing step sizes. Can measure PCE.

https://www.ti.com/lit/ds/symlink/ina219.pdf

https://cdn-shop.adafruit.com/datasheets/mcp4725.pdf

https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf


[Git Command Line no Login](https://stackoverflow.com/questions/35942754/how-can-i-save-username-and-password-in-git#35942890)

https://forum.arduino.cc/t/serial-input-basics-updated/382007

https://www.electroschematics.com/simple-microampere-meter-circuit/

https://www.eevblog.com/forum/beginners/reading-micro-amp-current-output-of-a-sensor/

https://training.ti.com/ti-precision-labs-current-sense-amplifiers-current-sensing-different-types-amplifiers?context=1139747-1139745-1138708-1139729-1138709

https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/wiring-and-test

Mppt measurement

https://onlinelibrary.wiley.com/doi/full/10.1002/solr.201800287?saml_referrer

https://pubs.rsc.org/en/content/articlelanding/2017/tc/c7tc03482b

to buy
https://www.amazon.com/AITRIP-PCSTCA9548A-Multiplexer-Breakout-Expansion/dp/B08JGSMRF9/ref=pd_lpo_1?pd_rd_i=B08JGSMRF9&th=1

https://www.amazon.com/BOJACK-PC817-OPTOCOUPLER-Installation-PC817C/dp/B08CXRHDHP/ref=sr_1_8?crid=7WPI1A2T7QOM&keywords=optocoupler&qid=1657751883&sprefix=optocoupler%2Caps%2C54&sr=8-8


# Conda

to create environment.yml file, navigate to Stability-Setup directory and then run:

```
conda env export > environment.yml
```

to create new environment from yml file:

```
conda env create -f environment.yml
```

to update environment from yml file:

```
conda env update --prefix ./env --file environment.yml  --prune
```

  - vs2015_runtime=14.27.29016=h5e58377_2
