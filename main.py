print("Menu\n a)Play a video\n b)save video without audio\n c)timestamp")
print("Please save your video file in root/home folder as sample.mp4")
choice=input("Enter your choice")
if choice == 1 :
	import videoplay
elif choice == 2 :
	import wo_audit
elif choice ==3 :
	import timestamp
else :
	pass
