// Empêche une fenêtre de console supplémentaire sous Windows en version publiée.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    fontaine_lib::run()
}
