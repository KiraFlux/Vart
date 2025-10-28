#include "VartPages.hpp"

#include "bytelang/primitive.hpp"
#include "misc/Macro.hpp"
#include "ui2/impl/widget/Builtin.hpp"
#include "vart/Device.hpp"
#include "vart/util/Vector2D.hpp"

using ui2::impl::page::PrintingPage;
using vart::Vector2D;
using Mode = vart::Planner::Mode;
using vart::Device;

using bytelang::primitive::i8;
using namespace ui2::impl::widget;

constexpr const SpinBox<i8>::Settings offsets_settings = {-120, 120, 5};
constexpr const Mode moving = Mode::Accel;
constexpr const Mode offseting = Mode::Position;

static Vector2D target_pos{0, 0};

static void moveToTarget(Mode mode) {
  auto& p = Device::getInstance().planner;
  p.setMode(mode);
  p.moveTo(target_pos);
}

ui2::impl::page::HomingPage::HomingPage() : abc::Page("Homing") {
  auto& c = Device::getInstance().planner.getController();

  add(new CheckBox(Text("Enable"), [&c](bool e) { c.setEnabled(e); }));
  add(new Button(Text("Pull Out"), [&c]() { c.pullRopesOut(); }));
  add(new Button(Text("Pull In"), [&c]() { c.pullRopesIn(); }));
  add(new Button(Text("Set Home"), [&c]() { c.setCurrentPositionAsHome(); }));

  add(new Button(Text("Move Top"), [&c]() {
    target_pos = {0, c.getAreaSize().y / 2.0};
    moveToTarget(moving);
  }));

  add(new Button(Text("Move Home"), []() {
    target_pos = {0, 0};
    moveToTarget(moving);
  }));

  // offsets

  static SpinBox<i8> spin_left(offsets_settings, 0, [&c](i8 o) {
    c.setLeftOffset(o);
    moveToTarget(offseting);
  });
  add(new Named(Text("Left-Offset MM"), spin_left));

  static SpinBox<i8> spin_right(offsets_settings, 0, [&c](i8 o) {
    c.setRightOffset(o);
    moveToTarget(offseting);
  });
  add(new Named(Text("Right-Offset MM"), spin_right));
}