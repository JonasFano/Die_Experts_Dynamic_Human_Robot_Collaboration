class ABFilter:
    def __init__(self, alpha=0.1, beta=0.05, dt=1.0):
        self.alpha = alpha
        self.beta = beta
        self.x_prev = None  # Initial x position estimate
        self.y_prev = None  # Initial y position estimate
        self.Vx_prev = None  # Initial velocity in x direction
        self.Vy_prev = None  # Initial velocity in y direction
        self.dt = dt

    def filter(self, new_pos):
  
        x_meas, y_meas = new_pos

        x, Vx = self.filter_step(self.alpha, self.beta, x_meas, self.dt, self.x_prev, self.Vx_prev)
        y, Vy = self.filter_step(self.alpha, self.beta, y_meas, self.dt, self.y_prev, self.Vy_prev)
  
        self.x_prev = x
        self.y_prev = y
        self.Vx_prev = Vx
        self.Vy_prev = Vy

        return (x, y)
    
    def filter_step(self, alpha, beta, meas, dt, x_prev, V_prev):
      
        if x_prev is None and V_prev is None:
            return meas, 0.0
        
        # Predict the new position using the previous position and velocity
        x_pred = x_prev + (V_prev * dt)
        V_pred = V_prev
        
        # Update the position and velocity using the measurement
        x = x_pred + (alpha * (meas - x_pred))
        V = V_pred + ((beta / dt) * (meas - x_pred))
        
        return x, V


