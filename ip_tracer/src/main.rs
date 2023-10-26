use std::env;
use std::io::{self, Write};
use std::net::{IpAddr, TcpStream};
use std::str::FromStr;
use std::process;
use std::sync::mpsc::{Sender, channel};
use std::thread;



// const MAX_PORT:u32 = 65535;
const MAX_PORT:u32 = 100;

struct  Arguments {
    ip_address: IpAddr,
    nums_threads: u32
}

impl Arguments {
    fn new( args: &[String] ) -> Result< Arguments, &'static str> {
        if args.len() < 2 {
            return Err("Not enough argumnets, please use -h for help");

        } else if args.len() > 4 {
            return Err("too many argumnets, please use -h for help");
        }

        let ip: String = args[1].clone();
        
        if let Ok(ip_address) = IpAddr::from_str( &ip ) {
            if args[1].contains("-j") {
                let threads: u32 = match args[3].parse::<u32> (){
                    Ok(s) => s, 
                    Err(_) => return Err("Fail to parse thread number")
                };
                return Ok(Arguments { ip_address: ip_address, nums_threads: threads });
            } else {
                return Ok(Arguments { ip_address: ip_address, nums_threads: 4 });
            }
        } else {
            let flags = args[1].clone();
            if flags.contains("-h") || flags.contains("--help") && args.len() == 2 {
                print!("help"); // we can add the help info here.

            } else if flags.contains("-h") || flags.contains("--help") {
                return Err("too many argumnets!!");
            } else if flags.contains("-j") {
                let ip_address = match IpAddr::from_str(&args[3]) {
                    Ok(s) => s,
                    Err(_) => return Err("Not a Valid IP address, must be IPv4 or IPv6")
                };
                let threads = match args[2].parse::<u32> (){
                    Ok(s) => s,
                    Err(_) => return Err("Fail to parse thread number")
                };

                return Ok(Arguments { ip_address: (ip_address), nums_threads: (threads) });

            } else {
                return Err("Invalid syntax");
            }
        }
        
        return Err("Invalid syntax");

    }
    
}


fn scan( trx: Sender<u16>, start_port: u32, addr:IpAddr, threds: u32 ) {
    let mut port: u32 = start_port +1;
    loop {
        match TcpStream::connect( (addr, port as u16)) {
            Ok(_) => {
                print!(".");
                io::stdout().flush().unwrap();
                trx.send(port as u16).unwrap();
            }
            Err(_) => {}
        }

        if (MAX_PORT- port) <= threds {
            break;
        }
        port += threds;

    }

}


fn main() {

    let args: Vec<String> = env::args().collect();
    let program: String = args[0].clone();
    let argument = Arguments::new(&args).unwrap_or_else(
        |err| {
            if err.contains("help") {
                process::exit(0);
            } else {
                eprintln!("{} problem parsing arguments: {}", program, err);
                process::exit(0);
            }
        }

    );


    let num_threads = argument.nums_threads;
    let (tx, rx) = channel();
    for i in 0..num_threads {
        let tx = tx.clone();
        thread::spawn( move || { scan(tx, i, argument.ip_address, num_threads ); });
    }

    let mut out = vec![];
    drop(tx);
    for p in rx {
        out.push(p);
    }

    print!("");
    out.sort();
    for v in out {
        print!("{} is open", v);
    }

}
