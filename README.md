VerySeriousButton-vsbutil
=========================

"Service utility" for the Very Serious Button.
This code was originally intended for testing and initial programming of Very Serious Buttons during production. It is being provided as a tool for advanced users and a reference for those wishing to learn how the configuration interface works. No warranty is provided. Use at your own risk.

## Requires:
* Reasonably recent Windows, Linux or Mac OS X
* python-hidapi (https://pypi.python.org/pypi/hidapi/0.7.99-4)

## Usage:
See online help (```./vsbutil.py --help```)

## Examples:
    ./vsbutil.py setjoy
    ./vsbutil.py saveconfig

    ./vsbutil.py setkey ctrl+c;
    ./vsbutil.py saveconfig

    ./vsbutil.py setkeys shift+h e l l o comma space w o r l d shift+1

## Notes:
Configuration changes made by the "setjoy" or "setkey" commands are applied in RAM and will not persist across a reset unless you explicitly call the "saveconfig" command afterward. However, the "setkeys" command causes the configuration to be saved immediately
