#include "VartPages.hpp"

#include "ui2/impl/widget/Builtin.hpp"

using namespace ui2::impl::widget;

using ui2::impl::page::GamesPage;

GamesPage::GamesPage() : Page("VART-Combat") {
  static int clicks = 1;
  static Display<int> clicks_display(clicks);
  add(new Named(Text("Coins"), clicks_display));
  add(new Button(Text("}|{ |V| |/| !!!"), []() { clicks = (clicks + 1) * clicks; }));
}