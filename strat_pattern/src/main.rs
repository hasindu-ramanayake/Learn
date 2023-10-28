// App selling packages


struct AppInfo <T: VersionStrat > {
    feature_set: Vec< Box<dyn FeatureSet> >,
    package_type: T,
}

impl  < T: VersionStrat > AppInfo<T> {
    pub fn new( version: T ) ->Self {
        Self { feature_set: Vec::new(),  package_type: version }
    }

    fn add_feature(&mut self, feature: Box<dyn FeatureSet> ) {
        self.feature_set.push( feature);
    }

    fn print_all_features( &self){
        self.package_type.selling_strategy();
        println!("Contain Feature: " );
        for i in self.feature_set.iter() {
            i.print_features();
        }
    }
}
//----------------------------------------

trait FeatureSet {
    fn print_features(&self);
}

struct CamaraMode;
impl FeatureSet for CamaraMode {
    fn print_features(&self) {
        println!("\tCamara mode");
    }
}

struct AddFilterMode;
impl FeatureSet for AddFilterMode {
    fn print_features(&self) {
        println!("\tFilter mode");
    }
}

struct EditingMode;
impl FeatureSet for EditingMode {
    fn print_features(&self) {
        println!("\tediting mode");
    }
}

//we can put all the other Modes
//------------------------------------------------------------
trait VersionStrat {
    fn selling_strategy( &self);
}

struct FreeVersion;
impl  VersionStrat for FreeVersion {
    fn selling_strategy( &self) {
        println!("This is a free version");
    }
    
}

struct BasicVerison;
impl VersionStrat for BasicVerison {
    fn selling_strategy( &self) {
        println!("Monthly 4.99 Euros");
    }
}

struct  FullVersion;
impl VersionStrat for FullVersion {
    fn selling_strategy( &self) {
        println!("Monthly 14.99 Euros + Training");
    }
}


fn main() {
    let mut new_app = AppInfo::new(FreeVersion);
    new_app.add_feature( Box::new(CamaraMode) );
    new_app.print_all_features();

    println!("");
    let mut new_app2 = AppInfo::new(BasicVerison);
    new_app2.add_feature( Box::new(CamaraMode) );
    new_app2.add_feature( Box::new(AddFilterMode) );
    new_app2.print_all_features();

    println!("");
    let mut new_app3 = AppInfo::new(FullVersion);
    new_app3.add_feature( Box::new(CamaraMode) );
    new_app3.add_feature( Box::new(AddFilterMode) );
    new_app3.add_feature( Box::new(EditingMode) );
    new_app3.print_all_features();

}