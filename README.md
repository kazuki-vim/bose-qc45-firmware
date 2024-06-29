## Disclaimer
- Downgrading is not a officially supported action from Bose
- By following this manual, you need to take all responsibilities for bricking your own device.
- Currently this method is only tested on Windows

## TL;DR
There are 2 parts need to be executed:
- Part 1: Enable `Update Now` action on `btu.bose.com`
- Part 2: Override firmware file and update

### Part 1: Enable `Update Now` action
- Run `Bose Updater` then go to `btu.bose.com` , continue procedure till Update page
- Open console ( By right click -> Inspect -> choose `console` tab )
- Run below scripts
```js
// Enable `Advanced Mode` without pressing button
window.dispatchEvent(new Event('advancedmode_triggered'))

// Append the option to version dropdown list
document.getElementById('smartdevice_targetfirmware').appendChild(new Option('4.0.4-4360+de6a887', '4.0.4'));
```
## Part 2: Override firmware and update
- Download desired firmware from this repository, put into `C:\Users\<username>\AppData\Local\Temp` and renamed it to `bose.bin`
- Setup python-venv as you might want, and install dependencies
    ```bash
pip3 install -r requirements.txt
    ```
- Run script to detect firmware is downloaded and override that file with correct timing
```bash
py ./main.py
```
- After script is started, go to website and press `Update Now`
- Update will be carried on, and finally at 99%, status will be `Failed` with a warning shown (Don't panic! It's expected behavior)
- <i>You're done. The downgrading process is completed.</i>

## Background story
### 1. Why downgrading
- Bose has a long history of breaking their products by the firmware that they claimed "We've tested carefully by experts before rolling out to users".
- The current popular error with firmware ver `4.0.4-4360+de6a887` is
  - Power-on is inconsistent
  - Cannot play music via bluetooth
- There are various posts reporting this issue, but Bose never officially acknowledge.
https://www.reddit.com/r/bose/comments/1bkpbzj/update_messed_up_my_qc_45/
https://www.reddit.com/r/bose/comments/1bpkk68/no_sound_from_qc45_after_update/
https://www.reddit.com/r/bose/comments/1ccar8r/qc_45_stopped_working_after_software_update/
https://www.reddit.com/r/bose/comments/1c1zp69/qc45_no_sound/

### 2. Why need this manual
- There are some other great works from communitiy for variety of Bose devices:
https://github.com/bosefirmware/ced
https://github.com/bosefirmware/bose-dfu
- `bose-dfu` tool only gives support for devices whose firmware is in `dfu/xvu` format. 
- Unfortunatelly, Bose NC700 and Bose QC45 is not one of them, they consumes `bin` firmware.
- Moreover, with recent latest update of `btu` website and `Bose Updater` application, the most popular methods (cheating `Bose Updater` to fetch older firmware versions) is not working anymore.
- So the only possible method is to let `Bose Updater` download what it's allowed to download (latest firmware), then override firmware file with older firmware before `Bose Updater` trying to transfer firmware to device.

### 3. Steps

#### Firmware download
- There is no possible ways to get all the firmware version from `download.bose.com` anymore.
- Base on the latest firmware information, and previous firmware versions on the internet, I was able to download version `4.0.4` and `3.5.0`
```
<INDEX REVISION="01.00.00">
    <DEVICE ID="0x4039" PRODUCTNAME="Quietcomfort 45" USE_CLOUD="3">
        <HARDWARE REVISION="01.00.00">
            <RELEASE HTTPHOST="downloads.bose.com" LANGUAGES="en-us,es-mx,de,it,fr,zh-cn,nl,ja,pt-br,ru,pl" REVISION="4.0.4-4360+de6a887" URLPATH="/ced/duran/">
                <IMAGE CRC="0xBC4BFF13" FILENAME="duran_encrypted_prod_4.0.4-de6a887.bin" LENGTH="6075980" NOFORCE="1" REVISION="4.0.4-4360+de6a887" SUBID="0"/>
            </RELEASE>
        </HARDWARE>
    </DEVICE>
</INDEX>
```
- Production Code of Bose QC45 is `duran`
- The link to download firmware will have this format `https://downloads.bose.com/ced/duran/duran_encrypted_prod_<version>-<commit hash>.bin`
- If you guys can help me download older firmwares, please create PR

### Modify Bose btu website
If your Bose QC45 is on latest firmware already, Bose doesn't even allow you to select the latest version
This is written in their website source code
```
n.device.getAvailableVersions(function(e, t) {
    for (var r = device_targetfirmware.options.length, i = r - 1; i >= 0; i--)
        device_targetfirmware.remove(i);
    t.reverse();
}
```
Not being able to select version to update, means update action can't be done.
Hence, we need at least 1 option, which is the latest version of firmware.
Be notice that, if there is newer firmware version than 4.0.4, then `4.0.4-4360+de6a887` in `Option` html tag needs to be replaced with name of newer firmware version.

#### Python script
- Everytime `Bose Updater` downloads a firmware, it will rename firmware `bin` file to `Bose Updater.<nanoid>` , and save it to `C:\Users\<username>\AppData\Local\Temp`
- I've confirmed by checking hex content, basically `Bose Updater.<nanoid>` is a renamed version without any modification applied
- `Bose Updater` will follow these steps
  - Download firmware
  - Boot device to flash mode
  - Transfer firmware to device
```
# Logs located at C:\Users\<username>\AppData\Local\Temp\BoseUpdater.log
```
- So, the idea is to replace firmware file with desired firmware after file is completely downloaded, and before it's transferred to device.
- Python script would do:
  - Detect if new firmware file is downloaded
  - Wait until it's fully downloaded, override with desired firmware
*To be honest, I tried several methods to detect if firmware is completely downloaded, but it's hard to know, so from experience, I set delay time to 3.5s from when the file is originally created.*

#### Why update is failed
- The final step `Bose Updater` does after updating is to compare the original version `dtu.bose.com` sends to it, with device's current version
- Since those versions are different (we sent the latest version to it), result of updating will be failed
- But after you click `Try Again` on warning popup, new page will show and tell you that `There's an update available for your product!`, which means your device is running on older firmware

#### Some notes
- I'm not an expert in reverse-engineering and embeded-engineering, so I can't write a tool like `bose-dfu`
- However the good thing is we still use default `Bose Updater`, which avoids risks when transferring firmware to device
- If you like my work,T you can by me a coffee

#### Useful resources
- Thanks @bosefirmware (https://github.com/bosefirmware) to give me hope and ideas about downgrading firmware.
- Thanks @suzj and his great manual (https://github.com/sunzj/Way_of_Downgrade_BOSE_QC35ii) that gave me idea about overriding firmware file.
