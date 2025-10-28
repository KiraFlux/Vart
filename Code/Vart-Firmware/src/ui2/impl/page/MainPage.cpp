#include "VartPages.hpp"
#include "misc/Macro.hpp"


using ui2::impl::page::MainPage;

MainPage::MainPage() :
    Page("Main") {
    add(allocStatic(MediaPage()));
    add(allocStatic(WorkAreaPage()));
	add(allocStatic(HomingPage()));
    add(allocStatic(ToolServicePage()));
	add(allocStatic(MovementServicePage()));
	add(allocStatic(GamesPage()));
}

MainPage &MainPage::getInstance() {
    static MainPage instance;
    return instance;
}
