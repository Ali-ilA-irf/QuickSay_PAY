from PyQt5.QtWidgets import QStackedWidget, QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QAbstractAnimation, QEasingCurve, pyqtProperty

class FadingStackedWidget(QStackedWidget):
    """A custom QStackedWidget that crossfades between pages"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fade_time = 300  # ms
        self._animating = False

    def fade_to_index(self, index):
        if self._animating or self.currentIndex() == index:
            return

        self._animating = True
        
        next_widget = self.widget(index)
        
        # Apply opacity effect to the new widget
        self.next_effect = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(self.next_effect)
        self.next_effect.setOpacity(0.0)
        
        # Change to next widget immediately but keep it invisible
        self.setCurrentIndex(index)
        
        # Animate opacity from 0 to 1
        self.fade_in_anim = QPropertyAnimation(self.next_effect, b"opacity")
        self.fade_in_anim.setDuration(self.fade_time)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # When fade is done, reset state
        self.fade_in_anim.finished.connect(self._on_animation_finished)
        self.fade_in_anim.start(QAbstractAnimation.DeleteWhenStopped)

    def _on_animation_finished(self):
        self._animating = False
        # Remove effect to restore normal rendering pipeline performance
        self.currentWidget().setGraphicsEffect(None)
