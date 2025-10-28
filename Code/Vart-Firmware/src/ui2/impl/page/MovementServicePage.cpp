#include "VartPages.hpp"

#include "ui2/impl/widget/Builtin.hpp"
#include "misc/Macro.hpp"
#include "vart/Device.hpp"
#include "bytelang/primitive.hpp"


using M = vart::Planner::Mode;
using vart::Device;
using namespace bytelang::primitive;
using namespace ui2::impl::widget;

constexpr const SpinBox<i16>::Settings position_settings = {.min = -600, .max = 600, .step = 50};
constexpr const SpinBox<u8>::Settings speed_settings = {.min = 10, .max = 250, .step = 10};
constexpr const SpinBox<u8>::Settings accel_settings = {.min = 5, .max = 250, .step = 5};

static SpinBox<i16> spin_x(position_settings, 0);
static SpinBox<i16> spin_y(position_settings, 0);

#define ModeButton(mode) (__extension__( {static Button __b(Text(#mode), [&p](){p.setMode(mode);}); &__b;} ))

ui2::impl::page::MovementServicePage::MovementServicePage() :
    Page("Move Service") {
    auto &p = Device::getInstance().planner;

    // pos

    add(new Named(Text("Target-X"), spin_x));
    add(new Named(Text("Target-Y"), spin_y));
    add(new Button(Text("Move"), [&p](){
		p.moveTo({double(spin_x.value), double(spin_y.value)});
	}));

    // mode

    add( ModeButton(M::Position) );
    add( ModeButton(M::Speed) );
    add( ModeButton(M::Accel) );

    // set

    static SpinBox<u8> speed_in(speed_settings, u8(p.getSpeed()), [&p](u8 s) { p.setSpeed(s); });
    add(new Named(Text("Speed"), speed_in));
    static SpinBox<u8> accel_in(accel_settings, u8(p.getAccel()), [&p](u8 s) { p.setAccel(s); });
    add(new Named(Text("Accel"), accel_in));
}
