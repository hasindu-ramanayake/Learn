struct SpecificTarget;

impl SpecificTarget {
    fn specific_reuqest( &self ) -> String {
        "specific request".into()
    }
}
//-----------------------------------------------

trait Target {
    fn request( &self ) ->String;
}

struct NormalTarget;

impl Target for NormalTarget {
    fn request( &self ) ->String {
        "Normal Target".into()
    }
}

//-------------------------------------------------
struct TargetAdapter {
    adaptee: SpecificTarget,
}

impl TargetAdapter {
    fn new( adaptee: SpecificTarget ) ->Self {
        Self { adaptee}
    }

}

impl Target for TargetAdapter {
    fn request( &self ) ->String {
        self.adaptee.specific_reuqest()
    }
}

fn call_something( target: impl Target ) {
    println!("{}", target.request() );
}

fn main( ) {
    let target = NormalTarget;
    call_something(target);

    let adaptee = SpecificTarget;
    let adapter = TargetAdapter::new( adaptee );

    call_something(adapter);

}
