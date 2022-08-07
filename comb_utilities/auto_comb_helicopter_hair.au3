#include <MsgBoxConstants.au3>

$ScriptName = "Auto Comb Helicopter Hair";
If WinExists($ScriptName) Then Exit ; Make sure we don't launch this script twice.

AutoItWinSetTitle($ScriptName)

Global $g_bPaused = False
HotKeySet("{ESC}", "TogglePause")


Local $aPos = MouseGetPos()
$restrictX = $aPos[0]
$restrictY = $aPos[1]
Global $tooltipY = 0
$Height = @DesktopHeight
If $restrictY < 0 Then $tooltipY = -$Height


$retVal = MsgBox($MB_YESNO, $ScriptName, "This script will select each particle in the current hair system and make it stick out like a helicopter. It will likely take around 38 minutes to run." & @CRLF & _
										   @CRLF & _
										   "You should have already done the following:" & @CRLF & _
										   "     * Created a hair system with 360 particles sticking straight up" & @CRLF & _
										   "     * The camera should be looking directly down on the hair" & @CRLF & _
										   "     * The camera covers a large enough view so that the hairs can be pushed the whole way out" & @CRLF & _
										   "     * You are in Particle Edit mode" & @CRLF & _
										   "     * You have the Comb tool selected" & @CRLF & _
										   "     * The comb tool has a very large radius" & @CRLF & _
										   "     * The comb tool Strength is set to 1.000" & @CRLF & _
										   "     * Deflect Emitter is checked" & @CRLF & _
										   @CRLF & _
										   "Do you want to continue? If you click Yes, immediately move your mouse cursor over where the hair system is sticking up.")

If $retVal = $IDNO Then Exit

$timeStart = @HOUR & ":" & @MIN & ":" & @SEC

Sleep(5000)

WinActivate("Blender")

Sleep(2000)

ToolTip("Running script..." & @CRLF & "(Press ESC to pause.)", 0, $tooltipY, $ScriptName, 1)

; The mouse should be where the particles are.
; Store this position, as we'll want to go back to our original position when we're done placing a hair.
Local $originalMousePosition = MouseGetPos()

Send("!h")		; Unhide all the particles.
Send("^d")		; And deselect all the particles.

For $i=1 To 360
   ; Let's pick out a random hair.
   Send("l")
   Sleep(200)

   MouseClickDrag("left", $originalMousePosition[0], $originalMousePosition[1], $originalMousePosition[0] + 552, $originalMousePosition[1], 25)
   Sleep(500)

   ; Then do it again to truly flatten it out.
   MouseClickDrag("left", $originalMousePosition[0], $originalMousePosition[1], $originalMousePosition[0] + 552, $originalMousePosition[1], 25)
   Sleep(500)

   Send("h")				; Hide the current hair, so we don't accidentally ever click on it again.
   MouseMove($originalMousePosition[0], $originalMousePosition[1])		; Return to original position.
   Send("+^]")			; Call bpy.ops.rhhc.rotate_add_plus_deselect() (really, rhhc.rotate_add_plus_deselect) so we move to the next angle.
Next

Send("!h")		; Unhide all the particles.
Send("^d")		; And deselect all the particles.

ToolTip("")

MsgBox(0, "Done!", "Done! Elapsed time: " & _ElapsedTime($timeStart, @HOUR & ":" & @MIN & ":" & @SEC))
Exit

Func TogglePause()
   $g_bPaused = Not $g_bPaused
   If $g_bPaused Then
	  ToolTip("Script is paused." & @CRLF & "(Press ESC to unpause.)", 0, $tooltipY, $ScriptName, 1)
   Else
	  ToolTip("Running script..." & @CRLF & "(Press ESC to pause.)", 0, $tooltipY, $ScriptName, 1)
   EndIf

   While $g_bPaused
	  Sleep(100)
   WEnd
EndFunc

;===============================================================================
;
; Description:      Returns the difference in time. if $Oldtime>$Newtime it assumes a day has passed
; Parameter(s):     $Oldtime = in format of hour:min:sec "23:03:10"
;                   $NewTime = in format of hour:min:sec "01:03:09"
;
;===============================================================================
Func _ElapsedTime ( $OldTime, $NewTime )
	$old=StringSplit($OldTime,":")
	$new=StringSplit($NewTime,":" )
	$Oseconds=$old[3]+($old[2]*60)+($old[1]*3600)
	$Nseconds=$new[3]+($new[2]*60)+($new[1]*3600)
	if $Oseconds>$Nseconds then $Nseconds=$Nseconds+24*3600

	$outsec=$Nseconds-$Oseconds
	$hour=Int($outsec/3600)
	$min=Int(($outsec-($hour*3600))/60)
	$sec=$outsec-($hour*3600)-($min*60)
	$DiffTime = StringFormat("%02i:%02i:%02i", $hour,$min,$sec)
	return $DiffTime
EndFunc
