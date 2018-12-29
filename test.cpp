
#include "libtcod.hpp"


int main () 
{
  TCODConsole::initRoot(80,50,"libtcod C++ tutorial",false);
  TCODConsole* window = new TCODConsole(80, 50);
  while ( !TCODConsole::isWindowClosed() ) {
      TCOD_key_t key;
      TCODSystem::checkForEvent(TCOD_EVENT_KEY_PRESS,&key,NULL);
      window->clear();
      window->putChar(40,25,'@');
      TCODConsole::blit(window, 0, 0, 80, 50, TCODConsole::root, 0, 0, 0);
      TCODConsole::flush();
  }
  return 0;
}
