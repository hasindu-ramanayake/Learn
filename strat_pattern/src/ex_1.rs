// transport method

trait TransportStrategy {
    fn build_router(&self, from: &str, end:&str );
}

struct Warking;
impl TransportStrategy for Warking {
    fn build_router(&self, from: &str, end:&str ) {
        println!("I'm walking from: {} to {}", from, end);
    }
    
}

struct Vehical;
impl TransportStrategy for Vehical {
    fn build_router(&self, from: &str, end:&str ) {
        println!("I'm using a vehical from: {} to {}", from, end);
    }
}

struct Train;
impl  TransportStrategy for Train {
    fn build_router(&self, from: &str, end:&str ) {
        println!("I'm using Train from: {} to {}.", from, end);
    }
}


struct Navigator <T: TransportStrategy > {
    route_strategy: T
}

impl<T: TransportStrategy > Navigator<T> {
    pub fn new ( method: T ) ->Self {
        Self { route_strategy: method }
    }

    pub fn route( &self, from:&str, end: &str ) {
        self.route_strategy.build_router(from, end);
    }

}


fn main() {
    
    let nav1 = Navigator::new(Warking);
    nav1.route("home", "train station");
    
    let nav2 = Navigator::new(Train);
    nav2.route("train station", "office" );

    let nav3 = Navigator::new(Vehical);
    nav3.route("office", "home");
    
}
