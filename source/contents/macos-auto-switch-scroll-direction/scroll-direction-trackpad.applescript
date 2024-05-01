tell application "System Preferences"
	set current pane to pane "com.apple.preference.trackpad"
end tell

tell application "System Events"
	tell process "System Preferences"
		click radio button "Scroll & Zoom" of tab group 1 of window 1
		if (exists checkbox 1 of tab group 1 of window 1) then
			tell checkbox 1 of tab group 1 of window 1
				if value is 0 then click it
			end tell
		end if
	end tell
end tell

quit application "System Preferences"
