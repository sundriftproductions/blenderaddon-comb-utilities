#include <MsgBoxConstants.au3>

$ScriptName = "Comb Selected Hair";
If WinExists($ScriptName) Then Exit ; Make sure we don't launch this script twice.

AutoItWinSetTitle($ScriptName)

Global $g_bPaused = False
HotKeySet("{ESC}", "TogglePause")

$Direction = "D"; # Set this to "D" (to comb down), "U" (to comb up), "L" (to comb left), or "R" (to comb right).
$Strokes = 1
If $CmdLine[0] = 2 Then
   If $CmdLine[1] = "U" Then
	  $Direction = "U"
   ElseIf $CmdLine[1] = "L" Then
	  $Direction = "L"
   ElseIf $CmdLine[1] = "R" Then
	  $Direction = "R"
   EndIf

   If $CmdLine[2] = "2" Then
	  $Strokes = 2
   ElseIf $CmdLine[2] = "3" Then
	  $Strokes = 3
   EndIf
EndIf

Local $aPos = MouseGetPos()
$restrictX = $aPos[0]
$restrictY = $aPos[1]
Global $tooltipY = 0
$Height = @DesktopHeight
If $restrictY < 0 Then $tooltipY = -$Height

WinActivate("Blender")

ToolTip("Running script..." & @CRLF & "(Press ESC to pause.)", 0, $tooltipY, $ScriptName, 1)

; Move the mouse to the center of the application screen.
$WinLoc = WinGetPos("Blender")

If $Direction = "D" Then
   MouseMove($WinLoc[0]+($WinLoc[2]/2), $WinLoc[1]+($WinLoc[3]/4), 0) ; Start at 25% from the top of the screen.
ElseIf $Direction = "U" Then
   MouseMove($WinLoc[0]+($WinLoc[2]/2), $WinLoc[1]+($WinLoc[3]/2)+($WinLoc[3]/4), 0) ; Start at 25% from the bottom of the screen.
Else ; We're moving left or right, in which case we start at the center of the screen.
   MouseMove($WinLoc[0]+($WinLoc[2]/2), $WinLoc[1]+($WinLoc[3]/2), 0)
EndIf

; The mouse should be where the particles are.
; Store this position, as we'll want to go back to our original position when we're done placing a hair.
Local $originalMousePosition = MouseGetPos()

If $Direction = "D" Then
   For $i=1 To $Strokes
	  MouseClickDrag("left", $originalMousePosition[0], $originalMousePosition[1], $originalMousePosition[0], $originalMousePosition[1] + 540, 25)
	  Sleep(500)
   Next
   MouseMove($originalMousePosition[0], $originalMousePosition[1])		; Return to original position.
   Send("^{NUMPADADD}") ; Select a little more of the strand, if possible.
ElseIf $Direction = "U" Then
   For $i=1 To $Strokes
	  MouseClickDrag("left", $originalMousePosition[0], $originalMousePosition[1], $originalMousePosition[0], $originalMousePosition[1] - 540, 25)
	  Sleep(500)
   Next
   MouseMove($originalMousePosition[0], $originalMousePosition[1])		; Return to original position.
   Send("^{NUMPADADD}") ; Select a little more of the strand, if possible.
ElseIf $Direction = "R" Then
   For $i=1 To $Strokes
	  MouseClickDrag("left", $originalMousePosition[0], $originalMousePosition[1], $originalMousePosition[0] + 552, $originalMousePosition[1], 25)
	  Sleep(500)
   Next
   MouseMove($originalMousePosition[0], $originalMousePosition[1])		; Return to original position.
   ; Note that we don't select more of the strand when doing a left or right comb.
Else ; $Direction = "L" Then
   For $i=0 To $Strokes
	  MouseClickDrag("left", $originalMousePosition[0], $originalMousePosition[1], $originalMousePosition[0] - 552, $originalMousePosition[1], 25)
	  Sleep(500)
   Next
   MouseMove($originalMousePosition[0], $originalMousePosition[1])		; Return to original position.
   ; Note that we don't select more of the strand when doing a left or right comb.
EndIf

Send("+^[") ; Call rhhc.done_combing so the add-on turns off the X-ray (if appropriate).

ToolTip("")

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

