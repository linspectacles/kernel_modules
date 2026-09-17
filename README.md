# kernel_modules (legacy)
OBSOLETE PROGRAM. NEW VERSION: <a href="https://github.com/linspectacles/kernel_modules">https://github.com/linspectacles/kernel_modules</a>

Linux Kernel Modules Inspector, a python equivalent of the lsmod and modinfo commands

Hello, world!

<b>First things first?</b>
I am NOT A PROGRAMMER. I simply had fun prompting Gemini to output all the python codes you will find in this repository.

<b>OK, now about the concept?</b>
I wanted to create a GUI tool to easily visualise the kernel modules currently loaded by my OS, just to learn more about each one of them.

<img width="480" height="270" alt="Screenshot_20260730_112910" src="https://github.com/user-attachments/assets/268bcc2c-8a0c-4d60-be85-6e03da0d3cd8" />
<img width="480" height="270" alt="Screenshot_20260730_112831" src="https://github.com/user-attachments/assets/e7c29baa-4531-4e05-8bfe-6d8133893925" />

<b>OK, so what did I do?</b>
As I have no coding experience, I asked Gemini to code this for me so it came up with the ".py" files you see. 

<b>OK, now tell me about the files?</b>
The files in the "Main" branch are the latest and greatest. The files in the "Archive" branch were previous versions. All the versions uploaded here represent the evolution of the concept, for you to have a look and audit, use and fork, and do as you well please (I think I put it under GPL3). All versions were tested only on Fedora 44 KDE. I did not test this on any other DEs or non-systemd systems. I did not test this on any Arch/Debian-derivative either. But because they are written in python, I believe they should work cross-platform.

<b>OK, how do I run this?</b>
1. Ensure you have the required dependencies: python3.
2. Download the python file(s) you wish.
3. Ensure you're on the same directory of the file or navigate to it.
4. On the terminal, launch it by typing "python3" + the name of the file you want to try.
4. Alternatively, you can grant "executable" permissions to the file and launch it via your file manager.
5. Have fun!

<hr>
<p>I thought this was a fun little project so I decided to share it in case you find it fun/useful too. You can help me make it better, but I do not plan to spend much time on this project unless it really does take off. I have no clue about python (yet?). I am also new in GitHub so please be kind to me :-P</p>

# change log (legacy)
Active version of the kernel_modules under [https://github.com/linspectacles/kernel_modules]

<strong>Active version: Check "Main" branch. Legacy version change log:</strong>
- Version 11 (tested, OK) - Last Google Gemini version used as input for ChatGPT.
- Version 10 (tested, OK) - Added GPL license. Generated on Google Gemini.
- Version 9 (tested, OK) - Added persistence to light/dark theme preference. Generated on Google Gemini.
- Version 8 (tested, OK) - Changed the sorting label from "functional themes" to "categories" to improve clarity. Generated on Google Gemini.
- Version 7 (tested, OK) - Asked Gemini to have the modules "sorted" in categories. Generated on Google Gemini.
- Version 6 (tested, OK) - Made the active module counter be more explicitly stated at the top. Generated on Google Gemini.
- Version 5 (tested, OK) - Added some colour flair. Generated on Google Gemini.
- Version 4 (tested, OK) - Original GUI version. Generated on Google Gemini.
